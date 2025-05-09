import pytest
from playwright.sync_api import sync_playwright

from om11.task.captchas import (
    GeetestV3,
    GeetestV4,
    HCaptcha,
    ReCaptchaV2,
    ReCaptchaV3,
    Turnstile,
)

# Test URLs containing different CAPTCHA types
TEST_URLS = {
    "ReCaptchaV2": "https://www.google.com/recaptcha/api2/demo",
    "ReCaptchaV3": "https://recaptcha-demo.appspot.com/recaptcha-v3-request-scores.php",
    "HCaptcha": "https://accounts.hcaptcha.com/demo",
    "GeetestV3": "https://www.geetest.com/en/demo",
    "GeetestV4": "https://www.geetest.com/en/adaptive-captcha-demo",
    "Turnstile": "https://2captcha.com/demo/cloudflare-turnstile-challenge?__cf_chl_rt_tk=OEYEJAOUNBtbZMr6MTg9Js3VNyFD8VEEG0.JCVKOTUg-1746782860-1.0.1.1-D560sBa8g6CyiYvRj5J7OdXN69IPnO9FIQW_xR7i72U",
}


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set headless=True for CI
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


class TestCaptchaDetection:
    @pytest.mark.parametrize(
        "captcha_type,url",
        [
            ("ReCaptchaV2", TEST_URLS["ReCaptchaV2"]),
            ("ReCaptchaV3", TEST_URLS["ReCaptchaV3"]),
            ("HCaptcha", TEST_URLS["HCaptcha"]),
            ("GeetestV3", TEST_URLS["GeetestV3"]),
            ("GeetestV4", TEST_URLS["GeetestV4"]),
            ("Turnstile", TEST_URLS["Turnstile"]),
        ],
    )
    def test_detect_script_on_real_pages(self, page, captcha_type, url):
        """Test that each CAPTCHA type can be detected on its demo page"""
        page.goto(url)

        # Get the appropriate CAPTCHA class
        captcha_class = globals()[captcha_type]
        captcha = captcha_class()

        # Execute the detection script
        result = page.evaluate(captcha.DETECT_SCRIPT)

        # Verify detection worked
        assert result is not None, f"Failed to detect {captcha_type} on {url}"
        if captcha_type in ["ReCaptchaV2", "ReCaptchaV3"]:
            assert result.lower() in ["v2", "v3"]
        else:
            assert bool(result) is True

    @pytest.mark.parametrize(
        "captcha_type,url",
        [
            ("ReCaptchaV2", TEST_URLS["ReCaptchaV2"]),
            ("ReCaptchaV3", TEST_URLS["ReCaptchaV3"]),
            ("HCaptcha", TEST_URLS["HCaptcha"]),
            ("GeetestV3", TEST_URLS["GeetestV3"]),
            ("GeetestV4", TEST_URLS["GeetestV4"]),
            ("Turnstile", TEST_URLS["Turnstile"]),
        ],
    )
    def test_data_script_on_real_pages(self, page, captcha_type, url):
        """Test that data extraction works on each CAPTCHA type's demo page"""
        page.goto(url)

        # Get the appropriate CAPTCHA class
        captcha_class = globals()[captcha_type]
        captcha = captcha_class()

        # Execute the data script
        data = page.evaluate(captcha.DATA_SCRIPT)

        # Verify we got the expected data structure
        assert isinstance(data, dict), (
            f"Data script should return a dictionary for {captcha_type}"
        )

        # Verify required fields
        if captcha_type in ["ReCaptchaV2", "ReCaptchaV3", "HCaptcha", "Turnstile"]:
            assert "sitekey" in data, f"Missing sitekey in {captcha_type} data"
            assert data["sitekey"], f"Empty sitekey in {captcha_type} data"

        if captcha_type in ["ReCaptchaV3", "Turnstile"]:
            assert "action" in data, f"Missing action in {captcha_type} data"

        if captcha_type == "GeetestV3":
            assert "gt" in data, "Missing gt in GeetestV3 data"
            assert "challenge" in data, "Missing challenge in GeetestV3 data"

        if captcha_type == "GeetestV4":
            assert "captcha_id" in data, "Missing captcha_id in GeetestV4 data"
            assert "api_server" in data, "Missing api_server in GeetestV4 data"

    @pytest.mark.parametrize(
        "captcha_type,url",
        [
            ("ReCaptchaV2", TEST_URLS["ReCaptchaV2"]),
            ("ReCaptchaV3", TEST_URLS["ReCaptchaV3"]),
            ("HCaptcha", TEST_URLS["HCaptcha"]),
            ("Turnstile", TEST_URLS["Turnstile"]),
        ],
    )
    def test_submit_script_on_real_pages(self, page, captcha_type, url):
        """Test that submit scripts can set values in the page"""
        page.goto(url)

        # Get the appropriate CAPTCHA class
        captcha_class = globals()[captcha_type]
        captcha = captcha_class()

        # Test token value
        test_token = "test_token_123"

        # Execute the submit script
        page.evaluate(captcha.SUBMIT_SCRIPT, test_token)

        # Verify the value was set correctly
        if captcha_type in ["ReCaptchaV2", "ReCaptchaV3"]:
            value = page.evaluate(
                '() => document.querySelector("#g-recaptcha-response").value'
            )
            assert value == test_token
        elif captcha_type == "HCaptcha":
            value = page.evaluate(
                "() => document.querySelector('[name=\"h-captcha-response\"]').value"
            )
            assert value == test_token
        elif captcha_type == "Turnstile":
            value = page.evaluate(
                "() => document.querySelector('[name=\"cf-turnstile-response\"]').value"
            )
            assert value == test_token


# Additional negative tests
class TestNegativeCases:
    def test_no_captcha_detection(self, page):
        """Test that detection returns null on pages without CAPTCHAs"""
        page.goto("https://example.com")

        for captcha_class in [
            ReCaptchaV2,
            ReCaptchaV3,
            HCaptcha,
            GeetestV3,
            GeetestV4,
            Turnstile,
        ]:
            captcha = captcha_class()
            result = page.evaluate(captcha.DETECT_SCRIPT)
            assert result is None or result is False, (
                f"{captcha_class.__name__} incorrectly detected CAPTCHA"
            )
