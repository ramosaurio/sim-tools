from pySim.transport import ProactiveHandler
from pySim.cat import SendShortMessage, DeviceIdentities, Result, CommandDetails
from osmocom.utils import b2h


class FetchProactiveHandler(ProactiveHandler):

    STATUS_CODES  = {
        0x00: 'Acknowledged',
        0x01: 'Integrity/Cipher/MAC validation failed',
        0x02: 'Counter below threshold',
        0x03: 'Counter exceeded maximum',
        0x04: 'Counter access restricted',
        0x05: 'Encryption issue detected',
        0x06: 'Ambiguous security anomaly',
        0x07: 'Memory allocation denied',
        0x08: 'Execution requires delay',
        0x09: 'Target Application missing',
        0x0a: 'Security context insufficient',
        0x0b: 'Expecting response via SMS-SUBMIT',
        0x0c: 'Expecting response via SS-Request invoke'
    }

    def __init__(self):
        self.isProcessed = False
        self.stillMoreData = False
        self.parsedResponse = ''
        self.parsedCmdSw = ''

    def receive_fetch(self, pcmd):
        """Fallback si no hay un handler específico."""
        print("[!] Proactive command recibido pero no tiene handler específico:", type(pcmd).__name__)

        return self.prepare_response(pcmd, general_result='command_beyond_terminal_capability')

    def handle_SendShortMessage(self, pcmd):
        print("[SMS] Send Short Message solicitado")
        for child in pcmd.children:
            if child.__class__.__name__ == 'SMS_TPDU':
                self.isProcessed = True
                encoded_data = child.decoded.get('tpdu')
                offset = 0
                (resdata, cmdsw) = self.parse_envelope_response_data(encoded_data[offset:], self.stillMoreData)
                self.parsedCmdSw = cmdsw
                if (cmdsw == "6310"):
                    self.stillMoreData = True

                self.parsedResponse = self.parsedResponse + resdata
                self.parsedCmdSw = self.parsedCmdSw if self.stillMoreData is False else "6310"
        return self.prepare_response(pcmd, general_result='command_beyond_terminal_capability')



    def parse_response_data(self, data: str, has_more: bool = False):
        """Parse the full response data and extract payload + SW."""
        status_word = "9000"
        offset = 0

        offset = self._skip_tp_udhl(data, offset)

        if not has_more:
            if not self._is_simple_udhl(data):
                offset, status_word = self._parse_response_header(data, offset)

        return (data[offset:], status_word)

    def _skip_tp_udhl(self, data: str, offset: int) -> int:
        """Skip the TP-User Data Header Length."""
        tp_udhl = int(data[offset:offset + 2], 16)
        return offset + 2 + tp_udhl * 2

    def _is_simple_udhl(self, data: str) -> bool:
        """Check if TP-UDHL is minimal (5)."""
        tp_udhl = int(data[:2], 16)
        return tp_udhl == 5

    def _parse_response_header(self, data: str, offset: int) -> tuple:
        """Parse the response header fields and return updated offset and SW."""
        status_word = "9000"

        rpl = int(data[offset:offset + 4], 16)
        offset += 4

        rhl = int(data[offset:offset + 2], 16)
        offset += 2

        header = data[offset:offset + rhl * 2]
        offset += rhl * 2

        self._check_response_status(header)

        if rpl > rhl + 1:
            offset, status_word = self._extract_status_word(data, offset, header)

        return offset, status_word

    def _check_response_status(self, header: str):
        """Check and handle the status inside the header."""
        header_offset = 16  # After TAR (6 bytes) + CNTR (10 bytes)
        padding_count = header[header_offset:header_offset + 2]
        header_offset += 2
        response_status = int(header[header_offset:header_offset + 2], 16)

        if response_status != 0x00:
            message = self.STATUS_CODES.get(response_status, 'Unknown response status')
            if response_status not in (0x0b, 0x0c):
                raise RuntimeError(f"❌ Response Error: 0x{response_status:02X} - {message}")
            else:
                print(f"ℹ️ Informational Response: 0x{response_status:02X} - {message}")

    def _extract_status_word(self, data: str, offset: int, header: str) -> tuple:
        """Extract Status Word and adjust data if padding exists."""
        offset += 2  # Skip Command Counter
        status_word = data[offset:offset + 4]
        offset += 4

        pad_count = header[16:18]
        if pad_count != "00":
            pad_len = int(pad_count, 16) * 2
            remaining_data_len = len(data[offset:]) - pad_len
            data = data[offset:offset + remaining_data_len]
            offset = 0

        return offset, status_word
    def _handle_response_status(self, status: int):
        """Handle and print the response status."""
        if status != 0x00:
            message = self.STATUS_CODES.get(status, 'Unknown response status')
            if status not in (0x0b, 0x0c):
                raise RuntimeError(f"❌ Response Error: 0x{status:02X} - {message}")
            else:
                print(f"ℹ️ Informational Response: 0x{status:02X} - {message}")

    def parse_envelope_response_data(self, envelope_data: str, more_data: bool = False):
        idx = 0

        # Verificamos que comienza con un TPDU tipo SMS (0x41 = SMS-SUBMIT, TP-MTI)
        if envelope_data[idx:idx + 2] != "41":
            print("⚠️ WARN: Envelope data does not start with TPDU tag 0x41")
            return ('', '9000')

        # TPDU Parsing según TS 23.040
        tp_mti = int(envelope_data[idx:idx + 2], 16)
        tp_vpf = (tp_mti & 0x18) >> 3
        idx += 2

        tp_mr = int(envelope_data[idx:idx + 2], 16)  # TP-Message Reference
        idx += 2

        tp_da_len = int(envelope_data[idx:idx + 2], 16)  # TP-Destination Address length
        idx += 4 + tp_da_len + (tp_da_len % 2)  # Address Type (1 byte) + Address digits

        tp_pid = int(envelope_data[idx:idx + 2], 16)  # TP-Protocol ID
        idx += 2

        tp_dcs = int(envelope_data[idx:idx + 2], 16)  # TP-Data Coding Scheme
        idx += 2

        # TP-Validity Period
        if tp_vpf == 0x01 or tp_vpf == 0x03:  # enhanced or absolute
            idx += 14  # 7 bytes in hex
        elif tp_vpf == 0x02:  # relative
            tp_vp = int(envelope_data[idx:idx + 2], 16)
            idx += 2

        tp_udl = int(envelope_data[idx:idx + 2], 16)  # TP-User Data Length
        idx += 2

        # Procesar resto de datos
        return self.parse_response_data(envelope_data[idx:], more_data)

    def handle_DisplayText(self, decoded):
        print("[UI] Display Text")
        print("  -> Texto:", decoded.get('text', '<no text>'))
        return self.prepare_response(decoded, general_result='performed_successfully')

    def handle_SetUpMenu(self, decoded):
        print("[UI] Set Up Menu")
        items = decoded.get('menu_items', [])
        print("  -> Menú:", [item.get('text', '<no text>') for item in items])
        return self.prepare_response(decoded, general_result='performed_successfully')

    def handle_ProvideLocalInformation(self, decoded):
        print("[SYS] Provide Local Information")
        # Puedes simular aquí información de red, hora, etc.
        return self.prepare_response(decoded, general_result='performed_successfully')

    def handle_PollInterval(self, decoded):
        print("[SYS] Poll Interval:", decoded.get('duration', '<sin duración>'))
        return self.prepare_response(decoded, general_result='performed_successfully')

    def handle_MoreTime(self, decoded):
        print("[SYS] More Time solicitado")
        return self.prepare_response(decoded, general_result='performed_successfully')

    def handle_LaunchBrowser(self, decoded):
        print("[UI] Launch Browser")
        print("  -> URL:", decoded.get('url', '<no url>'))
        return self.prepare_response(decoded, general_result='performed_successfully')
