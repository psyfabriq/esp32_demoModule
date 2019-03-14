import random
import blink_module
import time
import _thread
from settings_modul import SettingsModule

from network_module import *

STATE_IS_CHANGE = False
DO_FINISH = False


def startChangeState(context: Context):
    global DO_FINISH
    DO_FINISH = True
    _thread.start_new_thread(_loopChangeState, (context,))


def _loopChangeState(context: Context):
    global STATE_IS_CHANGE
    global DO_FINISH
    while True:
        if STATE_IS_CHANGE and DO_FINISH:
            STATE_IS_CHANGE = False
            DO_FINISH = False
            context.doAction()
        time.sleep(1)


class State():
    def doAction(self, context: Context) -> str:
        raise NotImplementedError("You must override the method")


class LoadConfigState(State):
    def __init__(self) -> None:
        self._sm = SettingsModule()
        self._nm= NetworkModule(self._sm)

    def doAction(self, context: Context) -> str:
        if self._sm.getSetting(self._sm.GENERAL_CONFIG, 'uuid') is None:
            uuid = self.genUUID(8)
            self._sm.setSetting(self._sm.GENERAL_CONFIG, 'uuid', uuid)
            self._sm.setSetting(self._sm.GENERAL_CONFIG, 'wifi_ap_ssid', 'gmodule-' + uuid)
            self._sm.setSetting(self._sm.GENERAL_CONFIG, 'wifi_ap_pswd', "123456789")
            context.changeState(context.on_wifi_ap)
        else:
            context.changeState(context.on_wifi_client)

        context.setSettingsModule(self._sm)
        context.setNetworkModule(self._nm)
        blink_module.start_blink()
        return 'Config load OK!'

    def genUUID(self, l) -> str:
        chars = "abcdefghijklmnopqrstuvwxyz1234567890"
        uuid = ''
        for c in range(l):
            uuid += random.choice(chars)
        return uuid


class LoadAPWifiState(State):
    def doAction(self, context: Context) -> str:
        sm = context.sm
        ssid = sm.getSetting(sm.GENERAL_CONFIG, 'wifi_ap_ssid')
        pwd = sm.getSetting(sm.GENERAL_CONFIG, 'wifi_ap_pswd')
        context.nm.startWifiAp(ssid, pwd)
        blink_module.setIntervalBlink(0.2)
        return 'Load AP Wifi OK!'


class LoadClientWifiState(State):

    def doAction(self, context: Context) -> str:
        if context.sm.getSetting(context.sm.GENERAL_CONFIG, 'wifi_client_ssid') is None:
            context.errorState.setMessage('Not found settings Wifi Client', context, context.on_wifi_ap)
            return 'Load Client Wifi ERROR!'
        else:
            sm = context.sm
            ssid = sm.getSetting(sm.GENERAL_CONFIG, 'wifi_client_ssid')
            pwd = sm.getSetting(sm.GENERAL_CONFIG, 'wifi_client_pswd')
            url = sm.getSetting(sm.GENERAL_CONFIG, 'update_url')
            if url is not None:
                print('Start check update')
                context.nm.download_and_install_update_if_available(ssid, pwd, url)
            if not context.nm.startWifiClient(ssid, pwd):
                context.errorState.setMessage('Coud not conect to WiFi', context, context.on_wifi_ap)
                return 'Load Client Wifi ERROR!'
            else:
                context.changeState(context.on_mqtt_connect)
        return 'Load Client Wifi OK!'


class LoadMQTTState(State):

    def doAction(self, context: Context) -> str:
        return 'Load MQTT OK!'


class LoadSynchronizeTimeState(State):

    def doAction(self, context: Context) -> str:
        return 'Time Synchronize OK!'


class ErrorState(State):
    def __init__(self) -> None:
        self._msg = ''
        self._state = None

    def doAction(self, context: Context) -> str:
        context.changeState(self._state)
        s = self._msg
        self._msg = ''
        self._state = None
        return 'ERROR (%s)' % s

    def setMessage(self, msg, context: Context, state: State) -> None:
        self._msg = msg
        self._state = state
        context.changeState(self)


class Context(object):

    def __init__(self) -> None:
        self.errorState = ErrorState()
        self.on_load = LoadConfigState()
        self.on_wifi_ap = LoadAPWifiState()
        self.on_wifi_client = LoadClientWifiState()
        self.on_mqtt_connect = LoadMQTTState()
        self.on_time_synchronize = LoadSynchronizeTimeState()
        self.sm = None
        self.nm = None

    def startChangeState(self):
        startChangeState(self)

    def changeState(self, state: State) -> None:
        global STATE_IS_CHANGE
        self._state = state
        STATE_IS_CHANGE = True

    def doAction(self) -> None:
        self._execute('doAction')

    def setSettingsModule(self, sm: SettingsModule) -> None:
        self.sm = sm

    def setNetworkModule(self, nm: NetworkModule) -> None:
        self.nm = nm

    def _execute(self, operation: str) -> None:
        global DO_FINISH
        try:
            func = getattr(self._state, operation)
            print('Context {}.'.format(func(self)))
        except AttributeError:
            print('Context coud not do this')
        DO_FINISH = True

