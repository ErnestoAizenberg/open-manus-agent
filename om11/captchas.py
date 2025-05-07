class ReCaptchaV2:
    DETECT_SCRIPT = """() => {
        const recaptcha = document.querySelector('[data-sitekey]');
        if (recaptcha) {
            try {
                return grecaptcha && grecaptcha.getResponse ? 'v2' : null;
            } catch {
                return 'v2';
            }
        }
        return null;
    }"""

    DATA_SCRIPT = """() => ({
        sitekey: document.querySelector('[data-sitekey]').dataset.sitekey,
        url: location.href
    })"""

    SUBMIT_SCRIPT = """(token) => {
        document.querySelector('#g-recaptcha-response').value = token;
    }"""


class ReCaptchaV3:
    DETECT_SCRIPT = """() => {
        return document.querySelector('[data-sitekey]') && 
               !document.querySelector('[data-size]') ? 'v3' : null;
    }"""

    DATA_SCRIPT = """() => ({
        sitekey: document.querySelector('[data-sitekey]').dataset.sitekey,
        action: document.querySelector('[data-action]')?.dataset.action || 'verify',
        url: location.href
    })"""

    SUBMIT_SCRIPT = """(token) => {
        document.querySelector('#g-recaptcha-response').value = token;
    }"""


class HCaptcha:
    DETECT_SCRIPT = """() => document.querySelector('[data-hcaptcha]')"""

    DATA_SCRIPT = """() => ({
        sitekey: document.querySelector('[data-hcaptcha]').dataset.sitekey || 
                document.querySelector('iframe[src*="hcaptcha"]')?.src?.match(/sitekey=([^&]+)/)?.[1],
        url: location.href
    })"""

    SUBMIT_SCRIPT = """(token) => {
        document.querySelector('[name="h-captcha-response"]').value = token;
    }"""


class GeetestV3:
    DETECT_SCRIPT = """() => !!window.initGeetest"""
    DATA_SCRIPT = """() => ({
        gt: window.initGeetest.gt,
        challenge: window.initGeetest.challenge,
        url: location.href
    })"""
    SUBMIT_SCRIPT = """(s) => {
        document.querySelector('#g-recaptcha-response').value = s.token;
        if (window.callGeetest) window.callGeetest(s);
    }"""


class GeetestV4:
    DETECT_SCRIPT = """() => !!window.initGeetestV4"""
    DATA_SCRIPT = """() => ({
        captcha_id: window.initGeetestV4.captcha_id,
        api_server: window.initGeetestV4.api_server
    })"""
    SUBMIT_SCRIPT = """(s) => { window.gt4_validated = s.validate; }"""


class Turnstile:
    DETECT_SCRIPT = """() => document.querySelector('.cf-turnstile')"""
    DATA_SCRIPT = """() => ({
        sitekey: document.querySelector('.cf-turnstile').dataset.sitekey,
        action: document.querySelector('.cf-turnstile').dataset.action || 'default',
        url: location.href
    })"""
    SUBMIT_SCRIPT = """(token) => {
        document.querySelector('[name="cf-turnstile-response"]').value = token;
    }"""


class FunCaptcha:
    DETECT_SCRIPT = (
        """() => window.funcaptcha || document.querySelector('#FunCaptcha')"""
    )
    DATA_SCRIPT = """() => ({
        public_key: window.funcaptchaOptions?.publicKey || 
                  document.querySelector('[data-pkey]')?.dataset.pkey,
        url: location.href
    })"""
    SUBMIT_SCRIPT = """(token) => {
        document.querySelector('[name="fc-token"]').value = token;
    }"""
