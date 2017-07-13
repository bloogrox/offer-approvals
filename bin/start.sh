#!/bin/sh

nameko run --config nameko.yml \
    services.syncer:SyncerService \
    services.syncer_approvals_loader:SyncerApprovalsLoaderService \
    services.syncer_changes_detector:SyncerChangesDetectorService \
    services.approval_persistor:ApprovalPersistorService \
    services.emailer:EmailerService
