import logging 
import os

def init_logger():
    # Get the directory of the current file (src/utils) and go up to project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_file = os.path.join(base_dir, 'telegram_bot.log')
    
    logging.basicConfig(
        filename=log_file,  # Use absolute path
        filemode='a',        # Append mode
        format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO   # Minimum level to capture
    )

    # Add console logging too
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    # Set library loggers to WARNING to mask unnecessary INFO logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    
    logging.info(f"Logging initialized. Log file: {log_file}")
