from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Video


class TestHomePageMessage(TestCase):
    def test_app_title_message_shown_on_home_page(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Video Game Trailers')


class TestAddVideos(TestCase):
    def test_add_video(self):
        valid_video = {
            'name': 'Super Mario RPG',
            'url': 'https://www.youtube.com/watch?v=0r5PJx7rlds',
            'notes': 'Super Mario RPG trailer',
            'video_id': '0r5PJx7rlds'
        }
        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True)
        self.assertTemplateUsed('video_collection/video_list.html')
        self.assertContains(response, 'Super Mario RPG')
        self.assertContains(response, 'https://www.youtube.com/watch?v=0r5PJx7rlds')
        self.assertContains(response, 'Super Mario RPG trailer')

        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        video = Video.objects.first()
        self.assertEqual('Super Mario RPG', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=0r5PJx7rlds', video.url)
        self.assertEqual('Super Mario RPG trailer', video.notes)
        self.assertEqual('0r5PJx7rlds', video.video_id)

    def test_add_video_invalid_url_not_added(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            'https://minneapolis.edu',
            'https://minneapolis.edu?v=123456789'
        ]
        for invalid_video_url in invalid_video_urls:
            new_video = {
                'name': 'example',
                'url': invalid_video_url,
                'notes': 'example notes'
            }

            url = reverse('add_video')
            response = self.client.post(url, data=new_video)

            self.assertTemplateUsed('video_collection/add.html')

            messages = response.context['messages']
            message_texts = [message.message for message in messages]

            self.assertIn('Invalid YouTube URL', message_texts)
            self.assertIn('Please check the data entered', message_texts)

            video_count = Video.objects.count()
            self.assertEqual(0, video_count)


class TestVideoList(TestCase):
    def test_all_videos_displayed_in_correct_order(self):
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=101112')

        expected_video_order = [v2, v1, v3, v4]

        url = reverse('video_list')
        response = self.client.get(url)

        videos_in_template = list(response.context['videos'])
        self.assertEqual(videos_in_template, expected_video_order)

    def test_no_video_message(self):
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, 'No videos')
        self.assertEqual(0, len(response.context['videos']))

    def test_video_number_message_one_video(self):
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')

    def test_video_number_message_more_than_one_video(self):
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=101112')
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, '4 videos')


class TestVideoSearch(TestCase):
    pass


class TestVideoModel(TestCase):
    def test_invalid_url_raises_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch/something',
            'https://www.youtube.com/watch/something?v=12345',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            'https://minneapolis.edu',
            'https://minneapolis.edu?v=123456789'
        ]
        for invalid_video_url in invalid_video_urls:
            with self.assertRaises(ValidationError):
                Video.objects.create(name='example', url=invalid_video_url, notes='example note')

        self.assertEqual(0, Video.objects.count())

    def test_duplicate_video_raises_integrity_error(self):
        v1 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')


class TestVideoDetail(TestCase):
    def test_show_video_information(self):
        test_video = {
            'name': 'abc',
            'url': 'https://www.youtube.com/watch?v=123',
            'notes': 'example notes'
        }

        url = reverse('video_detail')
        response = self.client.get(url, data=test_video)
        # Check correct template was used
        self.assertTemplateUsed(response, 'video_collection/video_detail.html')

        # What data was sent to the template?
        # data_rendered = response.context['video']

        # Same as data sent to template?
        # self.assertEqual(data_rendered, test_video)

        # and correct data shown on page?
        self.assertContains(response, 'abc')
        self.assertContains(response, 'example notes')
        self.assertContains(response, 'https://www.youtube.com/watch?v=123')
