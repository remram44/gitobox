import os
import sys
try:
    from gitobox.main import main
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from gitobox.main import main


if __name__ == '__main__':
    main()
