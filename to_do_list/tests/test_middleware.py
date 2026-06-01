from django.test import TestCase, RequestFactory, override_settings
from django.utils import timezone
from to_do_list.middleware.timezone_middleware import TimezoneMiddleware


class TimezoneMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TimezoneMiddleware(lambda r: None)

    @override_settings(USE_TZ=True)
    def test_timezone_activated_from_cookie(self):
        request = self.factory.get("/")
        request.COOKIES["user_timezone"] = "Europe/Berlin"

        self.middleware(request)

        self.assertEqual(str(timezone.get_current_timezone()), "Europe/Berlin")

    @override_settings(USE_TZ=True)
    def test_invalid_timezone_deactivates(self):
        request = self.factory.get("/")
        request.COOKIES["user_timezone"] = "invalid/tz"

        self.middleware(request)

        self.assertFalse(timezone.is_aware(timezone.now()) is False)
