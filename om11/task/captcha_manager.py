import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple

import aiohttp

from om11.task.captchas import (
    FunCaptcha,
    GeetestV3,
    GeetestV4,
    HCaptcha,
    ReCaptchaV2,
    ReCaptchaV3,
    Turnstile,
)


# --- CAPTCHA TYPE DEFINITIONS ---
class CaptchaType(Enum):
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3"
    HCAPTCHA = "hcaptcha"
    GEETEST_V3 = "geetest_v3"
    GEETEST_V4 = "geetest_v4"
    TURNSTILE = "turnstile"
    FUNCAPTCHA = "funcaptcha"
    IMAGE_CAPTCHA = "image_captcha"
    TEXT_CAPTCHA = "text_captcha"


# --- CAPTCHA PROVIDER CONFIG ---
CAPTCHA_PROVIDERS = {
    CaptchaType.RECAPTCHA_V2: {"main": "capmonster", "fallback": "anticaptcha"},
    CaptchaType.RECAPTCHA_V3: {"main": "capmonster", "fallback": "capsolver"},
    CaptchaType.HCAPTCHA: {"main": "capmonster", "fallback": "capsolver"},
    CaptchaType.FUNCAPTCHA: {"main": "capsolver", "fallback": "anticaptcha"},
    CaptchaType.TURNSTILE: {"main": "capsolver", "fallback": "anticaptcha"},
    CaptchaType.GEETEST_V3: {"main": "capsolver", "fallback": "anticaptcha"},
    CaptchaType.GEETEST_V4: {"main": "capsolver", "fallback": "anticaptcha"},
    CaptchaType.IMAGE_CAPTCHA: {"main": "capmonster", "fallback": "anticaptcha"},
    CaptchaType.TEXT_CAPTCHA: {"main": "capmonster", "fallback": "anticaptcha"},
}


@dataclass
class CaptchaSolution:
    token: str
    additional_data: Dict[str, Any] = None


# --- MAIN SOLVER CLASS ---
class CaptchaSolver:
    """
    Usage:
    ```python
    async with CaptchaSolver(page) as solver:
    api_keys = {
        "capmonster": "YOUR_CAPMONSTER_KEY",
        "anticaptcha": "YOUR_ANTICAPTCHA_KEY",
        "capsolver": "YOUR_CAPSOLVER_KEY"
    }
    await solver.solve(api_keys=api_keys)
    """

    def __init__(self, page):
        self.page = page
        self.session = aiohttp.ClientSession()
        self._captcha_cache: Dict[str, Tuple[str, Dict]] = {}
        self.captcha_classes = {
            CaptchaType.RECAPTCHA_V2: ReCaptchaV2,
            CaptchaType.RECAPTCHA_V3: ReCaptchaV3,
            CaptchaType.HCAPTCHA: HCaptcha,
            CaptchaType.TURNSTILE: Turnstile,
            CaptchaType.FUNCAPTCHA: FunCaptcha,
            CaptchaType.GEETEST_V3: GeetestV3,
            CaptchaType.GEETEST_V4: GeetestV4,
        }

    async def close(self):
        await self.session.close()

    async def detect(self) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Detect captcha and return type with parameters"""
        url = await self.page.url()
        cached_result = self._captcha_cache.get(url)

        if cached_result:
            print(f"Используем кэш для {url}: {cached_result[0]}")
            return cached_result

        for captcha_type, captcha_class in self.captcha_classes.items():
            if await self.page.evaluate(captcha_class.DETECT_SCRIPT):
                params = await self.page.evaluate(captcha_class.DATA_SCRIPT)
                self._captcha_cache[url] = (captcha_type, params)
                print(f"Кэш обновлён для {url}: {captcha_type}")
                return captcha_type, params
        return None

    async def solve(
        self,
        service: str = "auto",
        api_key: str = None,
        api_keys: Dict[str, str] = None,
    ) -> bool:
        detection_result = await self.detect()
        if not detection_result:
            return False  # captcha not detected

        captcha_type, params = detection_result
        supported_captcha_types = set(self.captcha_classes.keys())
        if captcha_type not in supported_captcha_types:
            raise ValueError(
                f"Detected captcha type '{captcha_type}' is not supported."
            )

        # Determine main service if 'auto'
        if service == "auto":
            main_service = CAPTCHA_PROVIDERS[captcha_type]["main"]
        else:
            main_service = service

        # Determine fallback service
        fallback_service = CAPTCHA_PROVIDERS[captcha_type]["fallback"]

        # Select API key for main and fallback
        # Assuming `api_keys` dict contains keys for all services
        main_api_key = None
        fallback_api_key = None
        if api_keys:
            main_api_key = api_keys.get(main_service)
            fallback_api_key = api_keys.get(fallback_service)
        else:
            main_api_key = api_key

        # First attempt with main service
        try:
            if main_api_key:
                solution = await self._solve_with_service(
                    main_service, captcha_type, main_api_key, params
                )
            else:
                raise ValueError(f"Invalid api key for service {main_service}.")
        except Exception as e:
            # Log or handle the exception
            print(f"Main service '{main_service}' failed: {e}")
            # Try fallback service
            try:
                self._captcha_cache.clear()

                detection_result = await self.detect()
                if not detection_result:
                    return False  # captcha not detected

                captcha_type, params = detection_result
                if fallback_api_key:
                    solution = await self._solve_with_service(
                        fallback_service, captcha_type, fallback_api_key, params
                    )
                else:
                    raise ValueError("Invalid api key for service {fallback_service}")
            except Exception as fallback_e:
                print(
                    f"Fallback service '{fallback_service}' also failed: {fallback_e}"
                )
                raise  # re-raise the last exception

        # Submit solution
        captcha_class = self.captcha_classes[captcha_type]
        await self.page.evaluate(captcha_class.SUBMIT_SCRIPT, solution.__dict__)
        return True

    async def _solve_with_service(
        self,
        service: str,
        captcha_type: CaptchaType,
        api_key: str,
        params: Dict[str, Any],
    ) -> CaptchaSolution:
        """Route to appropriate solver based on service"""
        try:
            if service == "capmonster":
                return await self._solve_capmonster(captcha_type, api_key, params)
            elif service == "anticaptcha":
                return await self._solve_anticaptcha(captcha_type, api_key, params)
            elif service == "capsolver":
                return await self._solve_capsolver(captcha_type, api_key, params)
            else:
                raise ValueError(f"Unsupported service: {service}")
        except Exception:
            fallback_service = CAPTCHA_PROVIDERS[captcha_type]["fallback"]
            if fallback_service != service:
                return await self._solve_with_service(
                    fallback_service, captcha_type, api_key, params
                )
            raise

    # --- SERVICE IMPLEMENTATIONS ---
    async def _solve_capmonster(
        self, captcha_type: CaptchaType, api_key: str, params: Dict[str, Any]
    ) -> CaptchaSolution:
        """CapMonster Cloud API implementation"""
        url: str = "https://api.capmonster.cloud/createTask"
        data: Dict[str, Any] = {
            "clientKey": api_key,
            "task": {
                "websiteURL": params["url"],
                "type": self._get_capmonster_task_type(captcha_type),
            },
        }

        # Add type-specific parameters
        if captcha_type == CaptchaType.RECAPTCHA_V2:
            sitekey: str = params["sitekey"]
            data["task"]["websiteKey"] = sitekey
        elif captcha_type == CaptchaType.RECAPTCHA_V3:
            sitekey: str = params["sitekey"]
            data["task"]["websiteKey"] = sitekey
            data["task"]["minScore"] = 0.5
            data["task"]["pageAction"]: str = params.get("action", "verify")
        elif captcha_type == CaptchaType.HCAPTCHA:
            sitekey: str = params["sitekey"]
            data["task"]["websiteKey"] = sitekey
        elif captcha_type == CaptchaType.TURNSTILE:
            sitekey: str = params["sitekey"]
            data["task"]["websiteKey"] = sitekey
            data["task"]["action"]: str = params.get("action", "default")
        elif captcha_type == CaptchaType.FUNCAPTCHA:
            data["task"]["websitePublicKey"]: str = params["public_key"]
        elif captcha_type == CaptchaType.GEETEST_V3:
            gt: str = params["gt"]
            challenge: str = params["challenge"]
            data["task"]["gt"] = gt

            data["task"]["challenge"] = challenge
        elif captcha_type == CaptchaType.GEETEST_V4:
            captcha_id: str = params["captcha_id"]
            data["task"]["gt"] = captcha_id
            data["task"]["version"] = 4

        async with self.session.post(url, json=data) as resp:
            result = await resp.json()
            if result.get("errorId", 0) > 0:
                raise RuntimeError(
                    f"CapMonster error: {result.get('errorDescription', 'Unknown error')}"
                )
            task_id = result["taskId"]

        return await self._poll_capmonster(api_key, task_id)

    async def _poll_capmonster(
        self, api_key: str, task_id: str, timeout: int = 120
    ) -> CaptchaSolution:
        """Poll CapMonster for solution"""
        url = "https://api.capmonster.cloud/getTaskResult"
        for _ in range(timeout // 5):
            await asyncio.sleep(5)
            async with self.session.post(
                url, json={"clientKey": api_key, "taskId": task_id}
            ) as resp:
                result = await resp.json()
                if result["status"] == "ready":
                    return CaptchaSolution(
                        token=result["solution"]["gRecaptchaResponse"]
                    )
                elif result["status"] == "failed":
                    raise RuntimeError("CapMonster task failed")
        raise TimeoutError("CapMonster timeout")

    async def _solve_anticaptcha(
        self, captcha_type: CaptchaType, api_key: str, params: Dict[str, Any]
    ) -> CaptchaSolution:
        """Anti-Captcha API implementation"""
        from python_anticaptcha import AnticaptchaClient
        from python_anticaptcha.tasks import (
            FunCaptchaTaskProxyless,
            GeeTestTaskProxyless,
            HCaptchaTaskProxyless,
            RecaptchaV2TaskProxyless,
            RecaptchaV3TaskProxyless,
        )

        client = AnticaptchaClient(api_key)

        if captcha_type == CaptchaType.RECAPTCHA_V2:
            task = RecaptchaV2TaskProxyless(
                website_url=params["url"], website_key=params["sitekey"]
            )
        elif captcha_type == CaptchaType.RECAPTCHA_V3:
            task = RecaptchaV3TaskProxyless(
                website_url=params["url"],
                website_key=params["sitekey"],
                min_score=0.5,
                page_action=params.get("action", "verify"),
            )
        elif captcha_type == CaptchaType.HCAPTCHA:
            task = HCaptchaTaskProxyless(
                website_url=params["url"], website_key=params["sitekey"]
            )
        elif captcha_type == CaptchaType.FUNCAPTCHA:
            task = FunCaptchaTaskProxyless(
                website_url=params["url"], website_public_key=params["public_key"]
            )
        elif captcha_type in (CaptchaType.GEETEST_V3, CaptchaType.GEETEST_V4):
            task = GeeTestTaskProxyless(
                website_url=params["url"],
                gt=(
                    params["gt"]
                    if captcha_type == CaptchaType.GEETEST_V3
                    else params["captcha_id"]
                ),
                challenge=params.get("challenge", ""),
                geetest_api_server=params.get("api_server", ""),
            )
        else:
            raise ValueError(
                f"Unsupported captcha type for Anti-Captcha: {captcha_type}"
            )

        job = client.createTask(task)
        solution = job.get_solution_response()
        return CaptchaSolution(token=solution["gRecaptchaResponse"])

    async def _solve_capsolver(
        self, captcha_type: CaptchaType, api_key: str, params: Dict[str, Any]
    ) -> CaptchaSolution:
        """CapSolver API implementation"""
        from python3_capsolver import FunCaptcha, GeeTest, HCaptcha, ReCaptcha

        if captcha_type == CaptchaType.RECAPTCHA_V2:
            solver = ReCaptcha(api_key=api_key)
            solution = await solver.aio_captcha_handler(
                websiteURL=params["url"], websiteKey=params["sitekey"]
            )
        elif captcha_type == CaptchaType.RECAPTCHA_V3:
            solver = ReCaptcha(api_key=api_key)
            solution = await solver.aio_captcha_handler(
                websiteURL=params["url"],
                websiteKey=params["sitekey"],
                version="v3",
                minScore=0.5,
                pageAction=params.get("action", "verify"),
            )
        elif captcha_type == CaptchaType.HCAPTCHA:
            solver = HCaptcha(api_key=api_key)
            solution = await solver.aio_captcha_handler(
                websiteURL=params["url"], websiteKey=params["sitekey"]
            )
        elif captcha_type == CaptchaType.FUNCAPTCHA:
            solver = FunCaptcha(api_key=api_key)
            solution = await solver.aio_captcha_handler(
                websiteURL=params["url"], websitePublicKey=params["public_key"]
            )
        elif captcha_type in (CaptchaType.GEETEST_V3, CaptchaType.GEETEST_V4):
            solver = GeeTest(api_key=api_key)
            solution = await solver.aio_captcha_handler(
                websiteURL=params["url"],
                gt=(
                    params["gt"]
                    if captcha_type == CaptchaType.GEETEST_V3
                    else params["captcha_id"]
                ),
                challenge=params.get("challenge", ""),
                version="4" if captcha_type == CaptchaType.GEETEST_V4 else "3",
            )
        else:
            raise ValueError(f"Unsupported captcha type for CapSolver: {captcha_type}")

        return CaptchaSolution(
            token=(
                solution["gRecaptchaResponse"]
                if "gRecaptchaResponse" in solution
                else solution["token"]
            ),
            additional_data=solution,
        )

    def _get_capmonster_task_type(self, captcha_type: CaptchaType) -> str:
        """Map captcha type to CapMonster task type"""
        mapping = {
            CaptchaType.RECAPTCHA_V2: "RecaptchaV2TaskProxyless",
            CaptchaType.RECAPTCHA_V3: "RecaptchaV3TaskProxyless",
            CaptchaType.HCAPTCHA: "HCaptchaTaskProxyless",
            CaptchaType.TURNSTILE: "TurnstileTaskProxyless",
            CaptchaType.FUNCAPTCHA: "FunCaptchaTaskProxyless",
            CaptchaType.GEETEST_V3: "GeeTestTaskProxyless",
            CaptchaType.GEETEST_V4: "GeeTestTaskProxyless",
        }
        return mapping.get(captcha_type, "NoCaptchaTaskProxyless")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
