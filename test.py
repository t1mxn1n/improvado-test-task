import unittest
from loguru import logger

from main import *

logger.add('debug_test.log', format='{time} {level} {message}',
           level='DEBUG', rotation='10 MB')

# Указать авторизованный токен
token = ''


class TestMain(unittest.TestCase):

    def test_check_correct_token(self):
        self.assertEqual(check_correct_token(token), True)
        self.assertEqual(check_correct_token('123'), False)
        logger.info('Successful check_correct_token')

    def test_get_result(self):
        self.assertEqual(get_result(token, '123'), None)
        self.assertEqual(get_result(token, '1'), None)
        self.assertEqual(type(get_result(token, 'dm')), list)
        logger.info('Successful get_result')

    def test_get_friends_by_offset(self):
        self.assertEqual(type(get_friends_by_offset(token, 'dm', 0)), Response)
        logger.info('Successful get_friends_by_offset')

    def test_account_info(self):
        self.assertEqual(account_info(token, 'dm')[1], True)
        self.assertEqual(account_info(token, 'qwe123qweasdasd')[1], False)
        logger.info('Successful account_info')

    def test_define_sex(self):
        self.assertEqual(define_sex(1), 'ж')
        self.assertEqual(define_sex(2), 'м')
        self.assertEqual(define_sex(3), '-')
        logger.info('Successful define_sex')

    def test_check_field(self):
        self.assertEqual(check_field({'city': {'title': '123'}}, 'city'), '123')
        self.assertEqual(check_field({'country': {'title': '123'}}, 'country'), '123')
        self.assertEqual(check_field({'bdate': '1.01.2000'}, 'bdate'), '2000-01-01')
        self.assertEqual(check_field({'bdate': '1.01.2000'}, 'unknown_fielf'), 'no data')
        logger.info('Successful check_field')

    def test_convert_to_iso(self):
        self.assertEqual(convert_to_iso('1.3'), '03-01')
        self.assertEqual(convert_to_iso('1.3.1999'), '1999-03-01')
        logger.info('Successful convert_to_iso')

    def test_add_zero(self):
        self.assertEqual(add_zero('1'), '01')
        self.assertEqual(add_zero('01'), '01')
        logger.info('Successful add_zero')


if __name__ == '__main__':
    unittest.main()
