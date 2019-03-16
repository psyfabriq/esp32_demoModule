import time
import network


from libs.ota_updater import OTAUpdater
from main.settings_module import SettingsModule
from libs.micro_web_srv import MicroWebSrv



WEB_SERVER = False
WIF_AP = False
SELF = None


class NetworkModule(object):

    def __init__(self, settings: SettingsModule):
        global SELF
        self.ap = network.WLAN(network.AP_IF)
        self.station = network.WLAN(network.STA_IF)
        self.srv = MicroWebSrv(webPath='www/')
        self.ap.active(False)
        self.station.active(False)
        self.srv.MaxWebSocketRecvLen = 256
        self.srv.WebSocketThreaded = False
        self.srv.AcceptWebSocketCallback = self._acceptWebSocketCallback
        self.startWebServer()
        self._settings = settings
        SELF = self

    def startWifiAp(self, ssid: str, pwd: str) -> bool:
        global WIF_AP
        self.stopWifiClient()
        if not WIF_AP:
            self.ap.active(True)
            self.ap.config(essid=ssid)
            self.ap.config(authmode=3, password=pwd)
            WIF_AP = True
        return True

    def stopWifiAp(self) -> None:
        global WIF_AP
        WIF_AP = False
        self.ap.active(False)

    def startWifiClient(self, ssid: str, pwd: str) -> bool:
        self.stopWifiAp()
        if not self.station.isconnected():
            self.station.active(True)
            self.station.connect(ssid, pwd)
            isconnected = False
            interval = 10
            while isconnected == False and interval > 0:
                isconnected = self.station.isconnected()
                interval -= 1
                print(interval)
                time.sleep(1)

            if isconnected:
                print('Connection successful')
                print(self.station.ifconfig())
            else:
                print('Connection error')
        return self.station.isconnected()

    def stopWifiClient(self) -> None:
        if self.station.isconnected():
            self.station.disconnect()
            self.station.active(False)

    def startWebServer(self) -> None:
        global WEB_SERVER
        if not WEB_SERVER:
            WEB_SERVER = True
            self.srv.Start(True)

    def stopWebServer(self) -> None:
        global WEB_SERVER
        WEB_SERVER = False
        self.srv.Stop()

    # ----------------------------------------------------------------------------
    @MicroWebSrv.route('/config')
    def _httpHandlerConfigGet(httpClient, httpResponse):
        global SELF
        content = SELF._settings.getListSettings(SELF._settings.GENERAL_CONFIG)
        httpResponse.WriteResponseJSONOk(content, None)

    @MicroWebSrv.route('/config', 'POST')
    def _httpHandlerConfigPost(httpClient, httpResponse):
        global SELF
        formData = httpClient.ReadRequestPostedFormData()
        SELF._settings.setSetitngs(SELF._settings.GENERAL_CONFIG, formData)
        httpResponse.WriteResponseRedirect('/')

    # ----------------------------------------------------------------------------

    # ----------------------------------------------------------------------------
    def _acceptWebSocketCallback(self, webSocket, httpClint):
        print("WS ACCEPT")
        webSocket.RecvTextCallback = self._recvTextCallback
        webSocket.RecvBinaryCallback = self._recvBinaryCallback
        webSocket.ClosedCallback = self._closedCallback

    def _recvTextCallback(self, webSocket, msg):
        print("WS RECV TEXT : %s" % msg)
        c = self._settings.getListSettings(self._settings.GENERAL_CONFIG)
        webSocket.SendText(str(c))

    def _recvBinaryCallback(self, webSocket, data):
        print("WS RECV DATA : %s" % data)

    def _closedCallback(self, webScket):
        print("WS CLOSED")

    # ----------------------------------------------------------------------------

    def download_and_install_update_if_available(self, ssid: str, pwd: str, url: str):
        o = OTAUpdater(url)
        o.download_and_install_update_if_available(ssid, pwd)
        time.sleep(5)
