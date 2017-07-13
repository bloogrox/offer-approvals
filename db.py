def get_approval_by_id(id_, db):
    return db.approvals.find_one({"_id": id_})
