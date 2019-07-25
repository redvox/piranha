import logging
import unittest
from unittest import mock
from unittest.mock import Mock

from piranha import ec2


def paging_mock(NextToken=None):
    if not NextToken:
        return {'AutoScalingGroups': [{'Name': 'asg1'}, {'Name': 'asg2'}],
                'NextToken': '123',
                'ResponseMetadata': {'HTTPStatusCode': 200}}
    if NextToken:
        return {'AutoScalingGroups': [{'Name': 'asg3'}],
                'ResponseMetadata': {'HTTPStatusCode': 200}}


class TestStart(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        logging.disable(logging.CRITICAL)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    @mock.patch('piranha.ec2.get_client')
    def test_get_autoscaling_groups(self, client_mock):
        client_mock.return_value = client_mock
        client_mock.describe_auto_scaling_groups.side_effect = paging_mock

        expected = [{'Name': 'asg1'}, {'Name': 'asg2'}, {'Name': 'asg3'}]
        self.assertEqual(expected, ec2.get_autoscaling_groups())

    @mock.patch('piranha.ec2.get_autoscaling_groups')
    def test_discover(self, mock):
        tags = [{'Key': 'Name',
                 'Value': 'service-core-develop'},
                {'Key': 'environment',
                 'Value': 'develop'},
                {'Key': 'service',
                 'Value': 'core'},
                {'Key': 'team',
                 'Value': 'awesome'}]

        mock.return_value = [{
            'AutoScalingGroupName': 'awesome1',
            'Tags': tags}, {
            'AutoScalingGroupName': 'awesome2',
            'LoadBalancerNames': ['Dog'],
            'Tags': tags}]

        expected = [{
            'asg': 'awesome1',
            'elb': None,
            'Name': 'service-core-develop',
            'environment': 'develop',
            'service': 'core',
            'team': 'awesome'
        }, {
            'asg': 'awesome2',
            'elb': 'Dog',
            'Name': 'service-core-develop',
            'environment': 'develop',
            'service': 'core',
            'team': 'awesome'
        }]
        self.assertEqual(expected, ec2.discover())
        self.assertEqual([], ec2.discover({'team': 'awesome'}))

    def test__extract_tags(self):
        asg_tags = {'Tags': [{'Key': 'Name',
                              'Value': 'service-core-develop'},
                             {'Key': 'environment',
                              'Value': 'develop'},
                             {'Key': 'service',
                              'Value': 'core'},
                             {'Key': 'team',
                              'Value': 'awesome'}]}

        expected = {
            'Name': 'service-core-develop',
            'environment': 'develop',
            'service': 'core',
            'team': 'awesome',
        }

        ec2._extract_tags(asg_tags)
        self.assertEqual(expected, ec2._extract_tags(asg_tags))

    def test__should_exclude(self):
        extracted_asg_tags = {
            'Name': 'service-core-develop',
            'environment': 'develop',
            'service': 'core',
            'team': 'awesome',
        }

        exclude_tags = {'team': 'awesome'}
        self.assertEqual(True, ec2._should_exclude(exclude_tags, extracted_asg_tags))
        exclude_tags = {'team': 'awesome', 'service': 'boring'}
        self.assertEqual(True, ec2._should_exclude(exclude_tags, extracted_asg_tags))
        exclude_tags = {'team': 'dog'}
        self.assertEqual(False, ec2._should_exclude(exclude_tags, extracted_asg_tags))
