class ImportdbRouter(object): 
    def db_for_read(self, model, **hints):
        "Point all operations on importdb models to 'centrinform'"
        if model._meta.app_label == 'importdb':
            return 'centrinform'
        return 'default'

    def db_for_write(self, model, **hints):
        "Point all operations on chinook models to 'centrinform'"
        if model._meta.app_label == 'importdb':
            return 'centrinform'
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        "Allow any relation if a both models in importdb app"
        if obj1._meta.app_label == 'importdb' and obj2._meta.app_label == 'importdb':
            return True
        # Allow if neither is importdb app
        elif 'importdb' not in [obj1._meta.app_label, obj2._meta.app_label]: 
            return True
        return False
    
    def allow_syncdb(self, db, model):
        if db == 'centrinform' or model._meta.app_label == "importdb":
            return False # we're not using syncdb on our legacy database
        else: # but all other models/databases are fine
            return True