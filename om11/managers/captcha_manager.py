import asyncio
import base64
import logging
import time
from enum import Enum
from typing import Any, Dict, Optional, Union

import requests
from capmonstercloudclient import CapMonsterClient, ClientOptions
from capmonstercloudclient.requests import (
    HcaptchaRequest,
    RecaptchaV2Request,
    RecaptchaV3ProxylessRequest,
)
from python_anticaptcha import AnticaptchaClient
from python_anticaptcha.tasks import (
    HCaptchaTaskProxyless,
    RecaptchaV2TaskProxyless,
    RecaptchaV3TaskProxyless,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CaptchaType(Enum):
    RECAPTCHA_V2 = "reCAPTCHA v2"
    RECAPTCHA_V3 = "reCAPTCHA v3"
    HCAPTCHA = "hCaptcha"
    IMAGE_CAPTCHA = "ImageCaptcha"
    TEXT_CAPTCHA = "TextCaptcha"
    UNKNOWN = "Unknown"


class CaptchaSolver:
    def __init__(self):
        self._page = None
        self.solvers = {
            "2captcha": self.solve_with_2captcha,
            "anticaptcha": self.solve_with_anticaptcha,
            "capmonster": self.solve_with_capmonster,
            "rucaptcha": self.solve_with_rucaptcha,
        }

    async def set_page(self, page):
        """Set the current page for captcha solving."""
        self._page = page

    async def detect_captcha_type(self) -> CaptchaType:
        """Detect the type of captcha on the current page."""
        if not self._page:
            raise Exception("Page not set. Call set_page() first.")

        try:
            # Check for reCAPTCHA v2/v3
            recaptcha_info = await self._page.evaluate(
                """
                () => {
                    const recaptcha = document.querySelector('[data-sitekey]');
                    if (recaptcha) {
                        try {
                            const version = grecaptcha && grecaptcha.getResponse 
                                ? 'v2' 
                                : 'v3';
                            return {
                                type: `reCAPTCHA ${version}`,
                                sitekey: recaptcha.dataset.sitekey
                            };
                        } catch (e) {
                            return {
                                type: 'reCAPTCHA v2',
                                sitekey: recaptcha.dataset.sitekey
                            };
                        }
                    }
                    return null;
                }
            """
            )

            if recaptcha_info:
                return (
                    (
                        CaptchaType.RECAPTCHA_V2
                        if "v2" in recaptcha_info["type"]
                        else CaptchaType.RECAPTCHA_V3
                    ),
                    recaptcha_info["sitekey"],
                )

            # Check for hCaptcha
            hcaptcha_info = await self._page.evaluate(
                """
                () => {
                    const hcaptcha = document.querySelector('[data-hcaptcha]');
                    if (hcaptcha) {
                        return {
                            type: 'hCaptcha',
                            sitekey: hcaptcha.dataset.sitekey || 
                                    document.querySelector('iframe[src*="hcaptcha"]')?.src?.match(/sitekey=([^&]+)/)?.[1]
                        };
                    }
                    return null;
                }
            """
            )

            if hcaptcha_info:
                return CaptchaType.HCAPTCHA, hcaptcha_info["sitekey"]

            # Check for simple image captcha
            image_captcha = await self._page.evaluate(
                """
                !!document.querySelector('img[src*="captcha"]')
            """
            )
            if image_captcha:
                return CaptchaType.IMAGE_CAPTCHA, None

            # Check for text captcha
            text_captcha = await self._page.evaluate(
                """
                !!document.querySelector('input[name*="captcha"]')
            """
            )
            if text_captcha:
                return CaptchaType.TEXT_CAPTCHA, None

            return CaptchaType.UNKNOWN, None
        except Exception as e:
            logger.error(f"Failed to detect captcha type: {str(e)}")
            raise Exception(f"Failed to detect captcha type: {str(e)}")

    async def solve_captcha(self, service: str, api_key: str, **kwargs) -> bool:
        """
        Solve captcha using specified service.

        Args:
            service: One of ['2captcha', 'anticaptcha', 'capmonster', 'rucaptcha']
            api_key: API key for the captcha solving service
            **kwargs: Additional parameters for specific captcha types

        Returns:
            bool: True if captcha was solved successfully
        """
        if service not in self.solvers:
            raise ValueError(f"Unsupported captcha service: {service}")

        captcha_type, sitekey = await self.detect_captcha_type()
        solver_func = self.solvers[service]

        return await solver_func(api_key, captcha_type, sitekey, **kwargs)

    async def solve_with_2captcha(
        self,
        api_key: str,
        captcha_type: CaptchaType,
        sitekey: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Solve captcha using 2Captcha service."""
        try:
            if captcha_type in [CaptchaType.RECAPTCHA_V2, CaptchaType.RECAPTCHA_V3]:
                if not sitekey:
                    raise Exception("No reCAPTCHA sitekey found on page")

                solver = TwoCaptchaSolver(api_key)
                page_url = self._page.url

                if captcha_type == CaptchaType.RECAPTCHA_V2:
                    result = await solver.solve_recaptcha_v2(
                        sitekey, page_url, **kwargs
                    )
                    await self._page.evaluate(
                        f"""
                        document.querySelector('#g-recaptcha-response').value = '{result}';
                    """
                    )
                else:  # RECAPTCHA_V3
                    result = await solver.solve_recaptcha_v3(
                        sitekey,
                        page_url,
                        kwargs.get("action", "verify"),
                        kwargs.get("min_score", 0.5),
                    )
                    await self._page.evaluate(
                        f"""
                        document.querySelector('#g-recaptcha-response').value = '{result}';
                    """
                    )

                return True

            elif captcha_type == CaptchaType.HCAPTCHA:
                if not sitekey:
                    raise Exception("No hCaptcha sitekey found on page")

                solver = TwoCaptchaSolver(api_key)
                result = await solver.solve_hcaptcha(sitekey, self._page.url)

                await self._page.evaluate(
                    f"""
                    document.querySelector('[name="h-captcha-response"]').value = '{result}';
                """
                )
                return True

            elif captcha_type == CaptchaType.IMAGE_CAPTCHA:
                image_data = await self._page.evaluate(
                    """
                    () => {
                        const img = document.querySelector('img[src*="captcha"]');
                        if (!img) return null;
                        
                        // Create canvas to get image data
                        const canvas = document.createElement('canvas');
                        canvas.width = img.width;
                        canvas.height = img.height;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0);
                        return canvas.toDataURL('image/png');
                    }
                """
                )

                if not image_data:
                    raise Exception("No image captcha found")

                solver = TwoCaptchaSolver(api_key)
                result = await solver.solve_image_captcha(image_data)

                # Find the input field and set the solution
                await self._page.evaluate(
                    f"""
                    () => {{
                        const inputs = [
                            ...document.querySelectorAll('input[name*="captcha"]'),
                            ...document.querySelectorAll('input[name*="verification"]')
                        ];
                        if (inputs.length > 0) {{
                            inputs[0].value = '{result}';
                        }}
                    }}
                """
                )
                return True

            else:
                raise Exception(
                    f"Unsupported captcha type for 2captcha: {captcha_type}"
                )

        except Exception as e:
            logger.error(f"Failed to solve captcha with 2captcha: {str(e)}")
            raise Exception(f"Failed to solve captcha with 2captcha: {str(e)}")

    async def solve_with_anticaptcha(
        self,
        api_key: str,
        captcha_type: CaptchaType,
        sitekey: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Solve captcha using Anti-Captcha service."""
        try:
            client = AnticaptchaClient(api_key)
            page_url = self._page.url

            if captcha_type == CaptchaType.RECAPTCHA_V2:
                if not sitekey:
                    raise Exception("No reCAPTCHA sitekey found on page")

                task = RecaptchaV2TaskProxyless(
                    website_url=page_url, website_key=sitekey, **kwargs
                )
                job = client.createTask(task)
                solution = job.get_solution_response()

                await self._page.evaluate(
                    f"""
                    document.querySelector('#g-recaptcha-response').value = '{solution['gRecaptchaResponse']}';
                """
                )
                return True

            elif captcha_type == CaptchaType.RECAPTCHA_V3:
                if not sitekey:
                    raise Exception("No reCAPTCHA sitekey found on page")

                task = RecaptchaV3TaskProxyless(
                    website_url=page_url,
                    website_key=sitekey,
                    min_score=kwargs.get("min_score", 0.5),
                    page_action=kwargs.get("action", "verify"),
                    **kwargs,
                )
                job = client.createTask(task)
                solution = job.get_solution_response()

                await self._page.evaluate(
                    f"""
                    document.querySelector('#g-recaptcha-response').value = '{solution['gRecaptchaResponse']}';
                """
                )
                return True

            elif captcha_type == CaptchaType.HCAPTCHA:
                if not sitekey:
                    raise Exception("No hCaptcha sitekey found on page")

                task = HCaptchaTaskProxyless(
                    website_url=page_url, website_key=sitekey, **kwargs
                )
                job = client.createTask(task)
                solution = job.get_solution_response()

                await self._page.evaluate(
                    f"""
                    document.querySelector('[name="h-captcha-response"]').value = '{solution['gRecaptchaResponse']}';
                """
                )
                return True

            elif captcha_type == CaptchaType.IMAGE_CAPTCHA:
                image_data = await self._page.evaluate(
                    """
                    () => {
                        const img = document.querySelector('img[src*="captcha"]');
                        if (!img) return null;
                        
                        const canvas = document.createElement('canvas');
                        canvas.width = img.width;
                        canvas.height = img.height;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0);
                        return canvas.toDataURL('image/png');
                    }
                """
                )

                if not image_data:
                    raise Exception("No image captcha found")

                # Implementation for image captcha with Anti-Captcha would go here
                raise NotImplementedError(
                    "Image captcha support for Anti-Captcha not implemented yet"
                )

            else:
                raise Exception(
                    f"Unsupported captcha type for Anti-Captcha: {captcha_type}"
                )

        except Exception as e:
            logger.error(f"Failed to solve captcha with Anti-Captcha: {str(e)}")
            raise Exception(f"Failed to solve captcha with Anti-Captcha: {str(e)}")

    async def solve_with_capmonster(
        self,
        api_key: str,
        captcha_type: CaptchaType,
        sitekey: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Solve captcha using CapMonster service."""
        try:
            client_options = ClientOptions(api_key=api_key)
            client = CapMonsterClient(options=client_options)
            page_url = self._page.url

            if captcha_type == CaptchaType.RECAPTCHA_V2:
                if not sitekey:
                    raise Exception("No reCAPTCHA sitekey found on page")

                request = RecaptchaV2Request(
                    websiteUrl=page_url, websiteKey=sitekey, **kwargs
                )
                solution = await client.solve_captcha(request)

                await self._page.evaluate(
                    f"""
                    document.querySelector('#g-recaptcha-response').value = '{solution['gRecaptchaResponse']}';
                """
                )
                return True

            elif captcha_type == CaptchaType.RECAPTCHA_V3:
                if not sitekey:
                    raise Exception("No reCAPTCHA sitekey found on page")

                request = RecaptchaV3ProxylessRequest(
                    websiteUrl=page_url,
                    websiteKey=sitekey,
                    minScore=kwargs.get("min_score", 0.5),
                    pageAction=kwargs.get("action", "verify"),
                    **kwargs,
                )
                solution = await client.solve_captcha(request)

                await self._page.evaluate(
                    f"""
                    document.querySelector('#g-recaptcha-response').value = '{solution['gRecaptchaResponse']}';
                """
                )
                return True

            elif captcha_type == CaptchaType.HCAPTCHA:
                if not sitekey:
                    raise Exception("No hCaptcha sitekey found on page")

                request = HcaptchaRequest(
                    websiteUrl=page_url, websiteKey=sitekey, **kwargs
                )
                solution = await client.solve_captcha(request)

                await self._page.evaluate(
                    f"""
                    document.querySelector('[name="h-captcha-response"]').value = '{solution['token']}';
                """
                )
                return True

            elif captcha_type == CaptchaType.IMAGE_CAPTCHA:
                # Implementation for image captcha with CapMonster would go here
                raise NotImplementedError(
                    "Image captcha support for CapMonster not implemented yet"
                )

            else:
                raise Exception(
                    f"Unsupported captcha type for CapMonster: {captcha_type}"
                )

        except Exception as e:
            logger.error(f"Failed to solve captcha with CapMonster: {str(e)}")
            raise Exception(f"Failed to solve captcha with CapMonster: {str(e)}")

    async def solve_with_rucaptcha(
        self,
        api_key: str,
        captcha_type: CaptchaType,
        sitekey: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Solve captcha using RuCaptcha service."""
        try:
            if captcha_type == CaptchaType.IMAGE_CAPTCHA:
                image_data = await self._page.evaluate(
                    """
                    () => {
                        const img = document.querySelector('img[src*="captcha"]');
                        if (!img) return null;
                        
                        const canvas = document.createElement('canvas');
                        canvas.width = img.width;
                        canvas.height = img.height;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0);
                        return canvas.toDataURL('image/png').split(',')[1];
                    }
                """
                )

                if not image_data:
                    raise Exception("No image captcha found")

                connection = RuCaptchaConnection(api_key)
                captcha = connection.send(("captcha.png", base64.b64decode(image_data)))
                solution = captcha.wait_decision()

                # Find the input field and set the solution
                await self._page.evaluate(
                    f"""
                    () => {{
                        const inputs = [
                            ...document.querySelectorAll('input[name*="captcha"]'),
                            ...document.querySelectorAll('input[name*="verification"]')
                        ];
                        if (inputs.length > 0) {{
                            inputs[0].value = '{solution}';
                        }}
                    }}
                """
                )
                return True

            elif captcha_type in [CaptchaType.RECAPTCHA_V2, CaptchaType.RECAPTCHA_V3]:
                if not sitekey:
                    raise Exception("No reCAPTCHA sitekey found on page")

                solver = RuCaptchaSolver(api_key)
                result = await solver.solve_recaptcha(
                    sitekey,
                    self._page.url,
                    is_v3=(captcha_type == CaptchaType.RECAPTCHA_V3),
                    **kwargs,
                )

                await self._page.evaluate(
                    f"""
                    document.querySelector('#g-recaptcha-response').value = '{result}';
                """
                )
                return True

            elif captcha_type == CaptchaType.HCAPTCHA:
                if not sitekey:
                    raise Exception("No hCaptcha sitekey found on page")

                solver = RuCaptchaSolver(api_key)
                result = await solver.solve_hcaptcha(sitekey, self._page.url)

                await self._page.evaluate(
                    f"""
                    document.querySelector('[name="h-captcha-response"]').value = '{result}';
                """
                )
                return True

            else:
                raise Exception(
                    f"Unsupported captcha type for RuCaptcha: {captcha_type}"
                )

        except Exception as e:
            logger.error(f"Failed to solve captcha with RuCaptcha: {str(e)}")
            raise Exception(f"Failed to solve captcha with RuCaptcha: {str(e)}")


class TwoCaptchaSolver:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://2captcha.com"
        self.session = requests.Session()

    async def solve_recaptcha_v2(self, sitekey: str, pageurl: str, **kwargs) -> str:
        params = {
            "key": self.api_key,
            "method": "userrecaptcha",
            "googlekey": sitekey,
            "pageurl": pageurl,
            "json": 1,
            **kwargs,
        }

        # Submit captcha
        submit_resp = self.session.post(f"{self.base_url}/in.php", data=params)
        submit_data = submit_resp.json()

        if submit_data.get("status") != 1:
            raise Exception(f"Failed to submit captcha: {submit_data.get('request')}")

        captcha_id = submit_data.get("request")

        # Wait for solution
        for _ in range(40):  # 40 attempts with 5 second delay = ~200 seconds timeout
            time.sleep(5)
            result_resp = self.session.get(
                f"{self.base_url}/res.php",
                params={
                    "key": self.api_key,
                    "action": "get",
                    "id": captcha_id,
                    "json": 1,
                },
            )
            result_data = result_resp.json()

            if result_data.get("status") == 1:
                return result_data.get("request")
            elif result_data.get("request") != "CAPCHA_NOT_READY":
                raise Exception(
                    f"Failed to solve captcha: {result_data.get('request')}"
                )

        raise Exception("Timeout while waiting for captcha solution")

    async def solve_recaptcha_v3(
        self,
        sitekey: str,
        pageurl: str,
        action: str = "verify",
        min_score: float = 0.5,
        **kwargs,
    ) -> str:
        params = {
            "key": self.api_key,
            "method": "userrecaptcha",
            "version": "v3",
            "googlekey": sitekey,
            "pageurl": pageurl,
            "action": action,
            "min_score": min_score,
            "json": 1,
            **kwargs,
        }

        return await self._solve_captcha(params)

    async def solve_hcaptcha(self, sitekey: str, pageurl: str, **kwargs) -> str:
        params = {
            "key": self.api_key,
            "method": "hcaptcha",
            "sitekey": sitekey,
            "pageurl": pageurl,
            "json": 1,
            **kwargs,
        }

        return await self._solve_captcha(params)

    async def solve_image_captcha(self, image_data: str, **kwargs) -> str:
        params = {
            "key": self.api_key,
            "method": "base64",
            "body": image_data,
            "json": 1,
            **kwargs,
        }

        return await self._solve_captcha(params)

    async def _solve_captcha(self, params: Dict[str, Any]) -> str:
        """Generic method to solve captcha with 2captcha."""
        # Submit captcha
        submit_resp = self.session.post(f"{self.base_url}/in.php", data=params)
        submit_data = submit_resp.json()

        if submit_data.get("status") != 1:
            raise Exception(f"Failed to submit captcha: {submit_data.get('request')}")

        captcha_id = submit_data.get("request")

        # Wait for solution
        for _ in range(40):  # 40 attempts with 5 second delay = ~200 seconds timeout
            time.sleep(5)
            result_resp = self.session.get(
                f"{self.base_url}/res.php",
                params={
                    "key": self.api_key,
                    "action": "get",
                    "id": captcha_id,
                    "json": 1,
                },
            )
            result_data = result_resp.json()

            if result_data.get("status") == 1:
                return result_data.get("request")
            elif result_data.get("request") != "CAPCHA_NOT_READY":
                raise Exception(
                    f"Failed to solve captcha: {result_data.get('request')}"
                )

        raise Exception("Timeout while waiting for captcha solution")


class RuCaptchaSolver:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://rucaptcha.com"
        self.session = requests.Session()

    async def solve_recaptcha(
        self,
        sitekey: str,
        pageurl: str,
        is_v3: bool = False,
        action: str = "verify",
        min_score: float = 0.5,
        **kwargs,
    ) -> str:
        params = {
            "key": self.api_key,
            "method": "userrecaptcha",
            "googlekey": sitekey,
            "pageurl": pageurl,
            "json": 1,
            **kwargs,
        }

        if is_v3:
            params.update({"version": "v3", "action": action, "min_score": min_score})

        # Submit captcha
        submit_resp = self.session.post(f"{self.base_url}/in.php", data=params)
        submit_data = submit_resp.json()

        if submit_data.get("status") != 1:
            raise Exception(f"Failed to submit captcha: {submit_data.get('request')}")

        captcha_id = submit_data.get("request")

        # Wait for solution
        for _ in range(40):  # 40 attempts with 5 second delay = ~200 seconds timeout
            time.sleep(5)
            result_resp = self.session.get(
                f"{self.base_url}/res.php",
                params={
                    "key": self.api_key,
                    "action": "get",
                    "id": captcha_id,
                    "json": 1,
                },
            )
            result_data = result_resp.json()

            if result_data.get("status") == 1:
                return result_data.get("request")
            elif result_data.get("request") != "CAPCHA_NOT_READY":
                raise Exception(
                    f"Failed to solve captcha: {result_data.get('request')}"
                )

        raise Exception("Timeout while waiting for captcha solution")

    async def solve_hcaptcha(self, sitekey: str, pageurl: str, **kwargs) -> str:
        params = {
            "key": self.api_key,
            "method": "hcaptcha",
            "sitekey": sitekey,
            "pageurl": pageurl,
            "json": 1,
            **kwargs,
        }

        # Submit captcha
        submit_resp = self.session.post(f"{self.base_url}/in.php", data=params)
        submit_data = submit_resp.json()

        if submit_data.get("status") != 1:
            raise Exception(f"Failed to submit captcha: {submit_data.get('request')}")

        captcha_id = submit_data.get("request")

        # Wait for solution
        for _ in range(40):  # 40 attempts with 5 second delay = ~200 seconds timeout
            time.sleep(5)
            result_resp = self.session.get(
                f"{self.base_url}/res.php",
                params={
                    "key": self.api_key,
                    "action": "get",
                    "id": captcha_id,
                    "json": 1,
                },
            )
            result_data = result_resp.json()

            if result_data.get("status") == 1:
                return result_data.get("request")
            elif result_data.get("request") != "CAPCHA_NOT_READY":
                raise Exception(
                    f"Failed to solve captcha: {result_data.get('request')}"
                )

        raise Exception("Timeout while waiting for captcha solution")
