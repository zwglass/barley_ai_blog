class DbDataHandle(object):
    """
    from zwutils_methods import DbDataHandle        # 数据库数据操作
    #    self.cls_dbdatahandle = DbDataHandle()        # 数据库数据操作
    """
    def __init__(self):
        pass

    def update_exists_db_list(self, check_key:str, update_data:list, db_data:list):
        # 更新数据库的数据
        ret_list = []
        for update_dict in update_data:
            exists_data = False
            for db_dict in db_data:
                if self.check_update_dict(check_key=check_key, update_dict=update_dict, db_dict=db_dict):
                    exists_data = True
                    ret_list.append({**db_dict, **update_dict})
            if not exists_data:
                ret_list.append(update_dict)
        return ret_list


    def check_update_dict(self, check_key:str, update_dict:dict, db_dict:dict) -> bool:
        # 验证是否是更新的数据
        return str(update_dict[check_key]) == str(db_dict[check_key])
