from unittest import TestCase
import datetime
import mock
from fitbit import Fitbit
from fitbit.exceptions import DeleteError

URLBASE = "%s/%s/user" % (Fitbit.API_ENDPOINT, Fitbit.API_VERSION)


class TestBase(TestCase):
    def setUp(self):
        self.fb = Fitbit(consumer_key='x', consumer_secret='y')

    def common_api_test(self, funcname, args, kwargs, expected_args, expected_kwargs):
        # Create a fitbit object, call the named function on it with the given
        # arguments and verify that make_request is called with the expected args and kwargs
        with mock.patch.object(self.fb, 'make_request') as make_request:
            retval = getattr(self.fb, funcname)(*args, **kwargs)
        args, kwargs = make_request.call_args
        self.assertEqual(expected_args, args)
        self.assertEqual(expected_kwargs, kwargs)


class APITest(TestBase):
    """Tests for python-fitbit API, not directly involved in getting authenticated"""

    def test_make_request(self):
        # If make_request returns a response with status 200,
        # we get back the json decoded value that was in the response.content
        fb = Fitbit(consumer_key='x', consumer_secret='y')
        ARGS = (1, 2)
        KWARGS = { 'a': 3, 'b': 4, 'headers': {'Accept-Language': fb.SYSTEM}}
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.content = "1"
        with mock.patch.object(fb.client, 'make_request') as client_make_request:
            client_make_request.return_value = mock_response
            retval = fb.make_request(*ARGS, **KWARGS)
        self.assertEqual(1, client_make_request.call_count)
        self.assertEqual(1, retval)
        args, kwargs = client_make_request.call_args
        self.assertEqual(ARGS, args)
        self.assertEqual(KWARGS, kwargs)

    def test_make_request_202(self):
        # If make_request returns a response with status 202,
        # we get back True
        fb = Fitbit(consumer_key='x', consumer_secret='y')
        mock_response = mock.Mock()
        mock_response.status_code = 202
        mock_response.content = "1"
        ARGS = (1, 2)
        KWARGS = { 'a': 3, 'b': 4, 'Accept-Language': fb.SYSTEM}
        with mock.patch.object(fb.client, 'make_request') as client_make_request:
            client_make_request.return_value = mock_response
            retval = fb.make_request(*ARGS, **KWARGS)
        self.assertEqual(True, retval)

    def test_make_request_delete_204(self):
        # If make_request returns a response with status 204,
        # and the method is DELETE, we get back True
        fb = Fitbit(consumer_key='x', consumer_secret='y')
        mock_response = mock.Mock()
        mock_response.status_code = 204
        mock_response.content = "1"
        ARGS = (1, 2)
        KWARGS = { 'a': 3, 'b': 4, 'method': 'DELETE', 'Accept-Language': fb.SYSTEM}
        with mock.patch.object(fb.client, 'make_request') as client_make_request:
            client_make_request.return_value = mock_response
            retval = fb.make_request(*ARGS, **KWARGS)
        self.assertEqual(True, retval)

    def test_make_request_delete_not_204(self):
        # If make_request returns a response with status not 204,
        # and the method is DELETE, DeleteError is raised
        fb = Fitbit(consumer_key='x', consumer_secret='y')
        mock_response = mock.Mock()
        mock_response.status_code = 205
        mock_response.content = "1"
        ARGS = (1, 2)
        KWARGS = { 'a': 3, 'b': 4, 'method': 'DELETE', 'Accept-Language': fb.SYSTEM}
        with mock.patch.object(fb.client, 'make_request') as client_make_request:
            client_make_request.return_value = mock_response
            self.assertRaises(
                DeleteError,
                fb.make_request,
                *ARGS,
                **KWARGS)

    def user_profile(self, user_id=None, data=None):
        """
        Get or Set a user profile. You can get other user's profile information
        by passing user_id, or you can set your user profile information by
        passing a dictionary of attributes that will be updated.

        .. note:
            This is not the same format that the GET comes back in, GET requests
            are wrapped in {'user': <dict of user data>}

        https://wiki.fitbit.com/display/API/API-Get-User-Info
        https://wiki.fitbit.com/display/API/API-Update-User-Info
        """
        if not user_id or data:
            user_id = '-'
        url = "%s/%s/user/%s/profile.json" % (self.API_ENDPOINT,
                                              self.API_VERSION, user_id)
        return self.make_request(url, data)

    def test_user_profile_get(self):
        fb = Fitbit(consumer_key='x', consumer_secret='y')
        user_id = "FOO"
        with mock.patch.object(fb, 'make_request') as make_request:
            make_request.return_value = 999
            retval = fb.user_profile_get(user_id)
        self.assertEqual(999, retval)
        args, kwargs = make_request.call_args
        url = "%s/%s/user/%s/profile.json" % (fb.API_ENDPOINT, fb.API_VERSION, user_id)
        self.assertEqual((url,), args)
        self.assertEqual({}, kwargs)

    def test_user_profile_update(self):
        fb = Fitbit(consumer_key='x', consumer_secret='y')
        data = "BAR"
        with mock.patch.object(fb, 'make_request') as make_request:
            make_request.return_value = 999
            retval = fb.user_profile_update(data)
        self.assertEqual(999, retval)
        args, kwargs = make_request.call_args
        url = "%s/%s/user/-/profile.json" % (fb.API_ENDPOINT, fb.API_VERSION)
        self.assertEqual((url, data), args)
        self.assertEqual({}, kwargs)


class CollectionResourceTest(TestBase):
    """Tests for _COLLECTION_RESOURCE"""
    def test_all_args(self):
        # If we pass all the optional args, the right things happen
        fb = Fitbit(consumer_key='x', consumer_secret='y')
        resource = "RESOURCE"
        date = datetime.date(1962, 1, 13)
        user_id = "bilbo"
        data = { 'a': 1, 'b': 2}
        with mock.patch.object(fb, 'make_request') as make_request:
            make_request.return_value = 999
            retval = fb._COLLECTION_RESOURCE(resource, date, user_id, data)
        self.assertEqual(999, retval)
        data['date'] = date
        args, kwargs = make_request.call_args
        url = "%s/%s/user/%s/%s.json" % (
            fb.API_ENDPOINT,
            fb.API_VERSION,
            user_id,
            resource,
        )
        self.assertEqual((url,data), args)
        self.assertEqual({}, kwargs)

    def test_date_string(self):
        # date can be a "yyyy-mm-dd" string
        fb = Fitbit(consumer_key='x', consumer_secret='y')
        resource = "RESOURCE"
        date = "1962-1-13"
        user_id = "bilbo"
        data = { 'a': 1, 'b': 2}
        with mock.patch.object(fb, 'make_request') as make_request:
            make_request.return_value = 999
            retval = fb._COLLECTION_RESOURCE(resource, date, user_id, data)
        self.assertEqual(999, retval)
        data['date'] = datetime.date(1962, 1, 13)
        args, kwargs = make_request.call_args
        url = "%s/%s/user/%s/%s.json" % (
            fb.API_ENDPOINT,
            fb.API_VERSION,
            user_id,
            resource,
            )
        self.assertEqual((url,data), args)
        self.assertEqual({}, kwargs)

    def test_no_date(self):
        # If we omit the date, it uses today
        fb = Fitbit(consumer_key='x', consumer_secret='y')
        resource = "RESOURCE"
        date = None
        user_id = "bilbo"
        data = { 'a': 1, 'b': 2}
        with mock.patch.object(fb, 'make_request') as make_request:
            make_request.return_value = 999
            retval = fb._COLLECTION_RESOURCE(resource, date, user_id, data)
        self.assertEqual(999, retval)
        data['date'] = datetime.date.today()  # expect today
        args, kwargs = make_request.call_args
        url = "%s/%s/user/%s/%s.json" % (
            fb.API_ENDPOINT,
            fb.API_VERSION,
            user_id,
            resource,
            )
        self.assertEqual((url,data), args)
        self.assertEqual({}, kwargs)

    def test_no_userid(self):
        # If we omit the user_id, it uses "-"
        fb = Fitbit(consumer_key='x', consumer_secret='y')
        resource = "RESOURCE"
        date = datetime.date(1962, 1, 13)
        user_id = None
        data = { 'a': 1, 'b': 2}
        expected_data = data.copy()
        expected_data['date'] = date.strftime("%Y-%m-%d")
        url = URLBASE + "/%s/%s.json" % (
            "-",  # expected user_id
            resource,
            )

        self.common_api_test('_COLLECTION_RESOURCE', (resource, date, user_id, data), {}, (url,expected_data), {})

    def test_no_data(self):
        # If we omit the data arg, it does the right thing
        resource = "RESOURCE"
        date = datetime.date(1962, 1, 13)
        user_id = "bilbo"
        data = None
        url = URLBASE + "/%s/%s/date/%s.json" % (
            user_id,
            resource,
            date,
            )
        self.common_api_test('_COLLECTION_RESOURCE', (resource,date,user_id,data), {}, (url,data), {})

    def test_body(self):
        # Test the first method defined in __init__ to see if it calls
        # _COLLECTION_RESOURCE okay - if it does, they should all since
        # they're all built the same way

        # We need to mock _COLLECTION_RESOURCE before we create the Fitbit object,
        # since the __init__ is going to set up references to it
        with mock.patch('fitbit.api.Fitbit._COLLECTION_RESOURCE') as coll_resource:
            coll_resource.return_value = 999
            fb = Fitbit(consumer_key='x', consumer_secret='y')
            retval = fb.body(date=1, user_id=2, data=3)
        args, kwargs = coll_resource.call_args
        self.assertEqual(('body',), args)
        self.assertEqual({'date': 1, 'user_id': 2, 'data': 3}, kwargs)
        self.assertEqual(999, retval)

class DeleteCollectionResourceTest(TestBase):
    """Tests for _DELETE_COLLECTION_RESOURCE"""
    def test_impl(self):
        # _DELETE_COLLECTION_RESOURCE calls make_request with the right args
        resource = "RESOURCE"
        log_id = "Foo"
        url = URLBASE + "/-/%s/%s.json" % (resource,log_id)
        self.common_api_test('_DELETE_COLLECTION_RESOURCE', (resource, log_id), {},
            (url,), {"method": "DELETE"})

    def test_cant_delete_body(self):
        fb = Fitbit(consumer_key='x', consumer_secret='y')
        self.assertFalse(hasattr(fb, 'delete_body'))

    def test_delete_water(self):
        log_id = "OmarKhayyam"
        with mock.patch('fitbit.api.Fitbit._DELETE_COLLECTION_RESOURCE') as delete_resource:
            delete_resource.return_value = 999
            fb = Fitbit(consumer_key='x', consumer_secret='y')
            retval = fb.delete_water(log_id=log_id)
        args, kwargs = delete_resource.call_args
        self.assertEqual(('water',), args)
        self.assertEqual({'log_id': log_id}, kwargs)
        self.assertEqual(999, retval)

class MiscTest(TestBase):

    def test_recent_activities(self):
        user_id = "LukeSkywalker"
        with mock.patch('fitbit.api.Fitbit.activity_stats') as act_stats:
            fb = Fitbit(consumer_key='x', consumer_secret='y')
            retval = fb.recent_activities(user_id=user_id)
        args, kwargs = act_stats.call_args
        self.assertEqual((), args)
        self.assertEqual({'user_id': user_id, 'qualifier': 'recent'}, kwargs)

    def test_activity_stats(self):
        user_id = "O B 1 Kenobi"
        qualifier = "frequent"
        url = URLBASE + "/%s/activities/%s.json" % (user_id, qualifier)
        self.common_api_test('activity_stats', (), dict(user_id=user_id, qualifier=qualifier), (url,), {})

    def test_activity_stats_no_qualifier(self):
        user_id = "O B 1 Kenobi"
        qualifier = None
        self.common_api_test('activity_stats', (), dict(user_id=user_id, qualifier=qualifier), (URLBASE + "/%s/activities.json" % user_id,), {})

    def test_timeseries(self):
        fb = Fitbit(consumer_key='x', consumer_secret='y')

        resource = 'FOO'
        user_id = 'BAR'
        base_date = '1992-05-12'
        period = '1d'
        end_date = '1998-12-31'

        # Not allowed to specify both period and end date
        self.assertRaises(
            TypeError,
            fb.time_series,
            resource,
            user_id,
            base_date,
            period,
            end_date)

        # Period must be valid
        self.assertRaises(
            ValueError,
            fb.time_series,
            resource,
            user_id,
            base_date,
            period="xyz",
            end_date=None)

        def test_timeseries(fb, resource, user_id, base_date, period, end_date, expected_url):
            with mock.patch.object(fb, 'make_request') as make_request:
                retval = fb.time_series(resource, user_id, base_date, period, end_date)
            args, kwargs = make_request.call_args
            self.assertEqual((expected_url,), args)

        # User_id defaults = "-"
        test_timeseries(fb, resource, user_id=None, base_date=base_date, period=period, end_date=None,
            expected_url="%s/1/user/-/FOO/date/1992-05-12/1d.json" % fb.API_ENDPOINT)
        # end_date can be a date object
        test_timeseries(fb, resource, user_id=user_id, base_date=base_date, period=None, end_date=datetime.date(1998, 12, 31),
            expected_url="%s/1/user/BAR/FOO/date/1992-05-12/1998-12-31.json" % fb.API_ENDPOINT)
        # base_date can be a date object
        test_timeseries(fb, resource, user_id=user_id, base_date=datetime.date(1992,5,12), period=None, end_date=end_date,
            expected_url="%s/1/user/BAR/FOO/date/1992-05-12/1998-12-31.json" % fb.API_ENDPOINT)

    def test_foods(self):
        def test_it(user_id, qualifier):
            url = "%s/%s/user/%s/foods/log/%s.json" % (
                Fitbit.API_ENDPOINT,
                Fitbit.API_VERSION,
                user_id if user_id else "-",
                qualifier,
                )
            self.common_api_test('%s_foods' % qualifier, [user_id], {}, (url,), {})
        test_it("user_id", "recent")
        test_it(None, "recent")
        test_it("Foo", "favorite")
        test_it("Bar", "frequent")

        url = URLBASE + "/-/foods/log/favorite/food_id.json"
        self.common_api_test('add_favorite_food', ('food_id',), {}, (url,), {'method': 'POST'})
        self.common_api_test('delete_favorite_food', ('food_id',), {}, (url,), {'method': 'DELETE'})

        url = URLBASE + "/-/foods.json"
        self.common_api_test('create_food', (), {'data': 'FOO'}, (url,), {'data': 'FOO'})
        url = URLBASE + "/-/meals.json"
        self.common_api_test('get_meals', (), {}, (url,), {})
