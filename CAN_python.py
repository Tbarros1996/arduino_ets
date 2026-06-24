#INTERFACE ARDUINO - PYTHON
#Desenvolvido por Thiago Barros



import requests
import serial
import time


class ETS2API:
    def __init__(self, url):
        self.url = url

    def fetch(self):
        return requests.get(self.url, timeout=1).json()


class DataNormalizer:
    @staticmethod
    def b(v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() == "true"
        return False


class DebugTable:

    @staticmethod
    def print(d):

        print("+-------------------+-------+")
        print("| Variável          | Valor |")
        print("+-------------------+-------+")

        for k, v in d.items():
            print(f"| {k:<17} | {v:<5} |")

        print("+-------------------+-------+\n")


class ETS2PanelBinary:

    def __init__(self, port):

        self.ser = serial.Serial(port, 115200, timeout=1)
        self.api = ETS2API(
            "http://192.168.56.1:25555/api/ets2/telemetry"
        )

        self.last_connected = False

    def build_packet(self, data):

        game = data["game"]
        truck = data["truck"]
        nav = data["navigation"]

        # -------------------------
        # painel
        # -------------------------
        C = DataNormalizer.b(game["connected"])
        E = DataNormalizer.b(truck["electricOn"])

        panel_on = C and E

        # -------------------------
        # setas
        # -------------------------
        L = DataNormalizer.b(truck.get("blinkerLeftActive", False))
        R = DataNormalizer.b(truck.get("blinkerRightActive", False))

        # -------------------------
        # luzes
        # -------------------------
        LOW = DataNormalizer.b(truck.get("lightsBeamLowOn", False)) if panel_on else 0
        HIGH = DataNormalizer.b(truck.get("lightsBeamHighOn", False)) if panel_on else 0

        # -------------------------
        # velocidade
        # -------------------------
        speed = float(truck.get("speed", 0))
        limit = float(nav.get("speedLimit", 0))
        SPD_WARN = 1 if limit > 0 and speed >= (0.8 * limit) else 0

        # -------------------------
        # combustível
        # -------------------------
        fuel = float(truck.get("fuel", 0))
        cap = float(truck.get("fuelCapacity", 1))

        ratio = fuel / cap if cap > 0 else 0

        F1 = 1 if ratio <= 1.0 and ratio > 0.5 else 0   # LOW (50–100%)
        F2 = 1 if ratio <= 0.5 and ratio > 0.1 else 0   # MEDIUM (10–50%)
        F3 = 1 if ratio <= 0.1 else 0                   # CRITICAL (<10%)

        # -------------------------
        # boot
        # -------------------------
        B = 0
        if panel_on and not self.last_connected:
            B = 1

        self.last_connected = panel_on

        # -------------------------
        # DEBUG
        # -------------------------
        DebugTable.print({
            "CONEXÃO": int(C),
            "ENERGIA": int(E),
            "BLINKER": int(B),
            "LEFT": int(L),
            "RIGHT": int(R),
            "LOW": int(LOW),
            "HIGH": int(HIGH),
            "SPEED": round(speed, 1),
            "LIMITE": round(limit, 1),
            "SPD_W": SPD_WARN,
            "FUEL": round(ratio * 100, 1),
            "F_LOW": F1,
            "F_MEDIUM": F2,
            "F_HIGH": F3
        })

        # -------------------------
        # BINÁRIO
        # -------------------------
        packet = bytes([
            0xAA,
            int(C),
            int(B),
            int(E),
            int(L),
            int(R),
            int(LOW),
            int(HIGH),
            int(SPD_WARN),
            int(F1),
            int(F2),
            int(F3)
        ])
        return packet

    def run(self):
        while True:
            try:
                data = self.api.fetch()
                packet = self.build_packet(data)
                self.ser.write(packet)
                time.sleep(0.05)

            except Exception as e:
                print("Erro:", e)
                time.sleep(0.2)


if __name__ == "__main__":
    ETS2PanelBinary("COM14").run()