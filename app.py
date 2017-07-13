import pymongo

from services.syncer import SyncerService  # NOQA
from services.emailer import EmailerService  # NOQA
from services.syncer_approvals_loader import SyncerApprovalsLoaderService  # NOQA
from services.syncer_changes_detector import SyncerChangesDetectorService  # NOQA
from services.approval_persistor import ApprovalPersistorService  # NOQA

import settings


mongo_client = pymongo.MongoClient(settings.MONGO_URI)
mongo_database = mongo_client.get_default_database()
