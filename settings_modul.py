import ujson
import os


class SettingsModule(object):
    """This Module Work with EPROM FLash , read and wirte setting app"""

    GENERAL_CONFIG = "config.json"
    LIST_SHEDULERS = "shedulers.json"
    LIST_RELAYS = "relays.json"

    def __init__(self):
        """Constructor"""

        self.checkIfExistConfFile(self.GENERAL_CONFIG, False)
        self.checkIfExistConfFile(self.LIST_SHEDULERS, True)
        self.checkIfExistConfFile(self.LIST_RELAYS, True)
        os.listdir()

    def checkIfExistConfFile(self, file_name, isList):
        """
        Method check file if exist
        """
        key = file_name.split('.')[0]
        f = open(file_name, 'a+')
        if isList:
            d = {key: []}
        else:
            d = {}

        if f.tell() == 0:
            print('a new file or the file was empty (%s)' % file_name)
            f.write(ujson.dumps(d))
        else:
            print('file existed, appending (%s)' % file_name)

        f.close()

    def setSetitngs(self, file_name, setting):
        """
        Method save settings
        """
        f = open(file_name, 'w')
        f.write(ujson.dumps(setting))
        f.close()
        return "%s save" % file_name

    def setSetting(self, file_name, key, value):
        """
        Method save settings
        """
        c = self.getListSettings(file_name)
        c[key] = value
        f = open(file_name, 'w')
        f.write(ujson.dumps(c))
        f.close()

        return "%s save" % file_name

    def getSetting(self, file_name, key):
        """
        Method get setting
        """
        c = self.getListSettings(file_name)
        if key in c.keys():
            v = c[key]
        else:
            v = None

        return v

    def getListSettings(self, file_name):
        """
        Method get List settings
        """
        f = open(file_name, 'r')
        c = ujson.loads(f.read())
        f.close()
        return c

    def removeSetting(self, file_name, key, isList):
        """
        Method remove setting
        """
        c = self.getListSettings(file_name)

        if isList:
            key_parent = file_name.split('.')[0]
            for x in c[key_parent][:]:
                v = ujson.loads(x)
            if v['id'] == key:
                c[key_parent].remove(x)
        else:
            c.pop(key)

        self.setSetitngs(file_name, c)
        return c

    def setSettingArr(self, file_name, key, value):
        """
        Method save settings
        insert object only like json
        """

        key_parent = file_name.split('.')[0]
        c = self.removeSetting(file_name, key, True)
        value['id'] = key
        c[key_parent].append(ujson.dumps(value))

        f = open(file_name, 'w')
        f.write(ujson.dumps(c))
        f.close()

        return "%s save" % file_name

    def getSettingArr(self, file_name, key):
        """
        Method get setting from array file config
        """
        key_parent = file_name.split('.')[0]
        v = None
        c = self.getListSettings(file_name)
        for x in c[key_parent][:]:
            k = ujson.loads(x)
            if k['id'] == key:
                c[key_parent].remove(x)
                v = k
        return v



if __name__ == "__main__":
    sm = SettingsModule()
    sm.setSetting(sm.GENERAL_CONFIG,'wifi_client_ssid','PFQHOME')
    sm.setSetting(sm.GENERAL_CONFIG,'wifi_client_pswd','97928980')




