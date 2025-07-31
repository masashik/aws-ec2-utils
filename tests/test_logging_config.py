import unittest
import logging
from ec2_utils import logging_config


class TestLoggingConfig(unittest.TestCase):

    def test_setup_logging(self):
        logger = logging_config.setup_logging()
        self.assertIsInstance(logger, logging.Logger)
        logger.info("This is a test log message.")

        # Confirm a handler is attached
        self.assertGreater(len(logger.handlers), 0)

if __name__ == "__main__":
    unittest.main()
