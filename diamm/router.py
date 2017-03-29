class DatabaseRouter(object):
    def db_for_read(self, model, **hints):
        "Point all operations on legacy models to 'migrate'"
        if model._meta.app_label == 'diamm_migrate':
            return 'migrate'
        return 'default'

    def db_for_write(self, model, **hints):
        "Point all operations on legacy models to 'migrate'"
        if model._meta.app_label == 'diamm_migrate':
            return 'migrate'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'diamm_migrate' and obj2._meta.app_label == 'diamm_migrate':
            return True

        elif 'diamm_migrate' not in [obj1._meta.app_label, obj2._meta.app_label]:
            return True

        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "diamm_migrate":
            return db == 'migrate'
        else: # but all other models/databases are fine
            return True
