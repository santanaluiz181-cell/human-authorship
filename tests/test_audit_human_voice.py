import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from audit_human_voice import audit_text  # noqa: E402


class TestAuditHumanVoice(unittest.TestCase):
    def test_empty_and_bom_only_input_return_complete_schema(self):
        for sample in ["", "   \n\t ", "\ufeff", "\ufeff   "]:
            res = audit_text(sample)
            self.assertEqual(res["status"], "EMPTY_INPUT")
            self.assertEqual(res["verdict"], "EMPTY_INPUT")
            self.assertEqual(res["authorship_gate_score"], 0)
            self.assertEqual(res["slop_hits"], [])

    def test_leading_bom_ignored_while_midtext_zerowidth_flagged(self):
        clean_bom = "\ufeffTexto curto. Aqui vai uma frase bem longa e detalhada com números de 2026 e fatos de campo para dar ritmo real."
        res_clean = audit_text(clean_bom)
        self.assertEqual(res_clean["zero_width_count"], 0)

        dirty = "Texto\u200b curto. Outra\ufeff frase de teste para checar."
        res_dirty = audit_text(dirty)
        self.assertEqual(res_dirty["zero_width_count"], 2)
        self.assertLessEqual(res_dirty["authorship_gate_score"], 75)

    def test_portuguese_and_english_slop_detected_case_insensitive(self):
        text = (
            "Vale ressaltar que os dados foram abertos. "
            "Além disso, devemos delve na tapestry do orçamento."
        )
        res = audit_text(text)
        self.assertGreaterEqual(len(res["slop_hits"]), 4)
        self.assertLessEqual(res["authorship_gate_score"], 65)

    def test_em_and_en_dashes_penalized(self):
        text = "Primeiro ponto \u2014 segundo ponto \u2013 terceiro ponto. Frase curta."
        res = audit_text(text)
        self.assertEqual(res["em_en_dash_count"], 2)
        self.assertEqual(res["authorship_gate_score"], 92)

    def test_low_burstiness_and_zero_short_sentences_fail_gate(self):
        uniform = " ".join(
            [
                "A equipe técnica revisou cada tabela de orçamento público publicada pelo órgão estadual ontem.",
                "O relatório preliminar indicou divergências relevantes entre os valores previstos inicialmente nos anexos.",
                "Os coordenadores locais decidiram enviar novos pedidos formais para esclarecer todas essas discrepâncias.",
                "A secretaria municipal respondeu somente depois do encerramento do prazo oficial combinado anteriormente.",
                "Os moradores da região sul aguardam medidas concretas antes do início do próximo semestre.",
            ]
        )
        res = audit_text(uniform)
        self.assertLess(res["burstiness_stdev"], 6.0)
        self.assertEqual(res["short_sentences_le8"], 0)
        self.assertLess(res["authorship_gate_score"], 80)
        self.assertNotEqual(res["verdict"], "PASS_HUMAN_RHYTHM")

    def test_varied_human_prose_passes_gate_cleanly(self):
        human = (
            "Faltou gás na terça. "
            "Juh abriu o depósito da associação no Aureny I às seis da manhã, contou três botijões vazios na fila e ligou para dois vizinhos antes da van escolar dobrar a esquina. "
            "Ninguém atendeu. "
            "Então ela tirou o cartão pessoal do bolso e pagou cento e vinte reais no mercadinho da quadra vizinha, sem recibo nem protocolo oficial. "
            "Deu tempo."
        )
        res = audit_text(human)
        self.assertEqual(res["verdict"], "PASS_HUMAN_RHYTHM")
        self.assertEqual(res["authorship_gate_score"], 100)
        self.assertEqual(res["slop_hits"], [])
        self.assertEqual(res["em_en_dash_count"], 0)

    def test_cli_json_and_missing_file_fail_fast(self):
        script = SCRIPTS_DIR / "audit_human_voice.py"
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "draft.md"
            draft.write_text("Silêncio oficial. A secretaria não respondeu ao protocolo enviado na terça.", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(script), str(draft), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertIn("authorship_gate_score", payload)

            empty_draft = Path(tmp) / "empty.md"
            empty_draft.write_text("", encoding="utf-8")
            proc_empty = subprocess.run(
                [sys.executable, str(script), str(empty_draft)],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(proc_empty.returncode, 0, msg=proc_empty.stderr)
            self.assertIn("EMPTY_INPUT", proc_empty.stdout)

        proc_missing = subprocess.run(
            [sys.executable, str(script), "Z:/nonexistent_file_check_999.md"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(proc_missing.returncode, 2)


if __name__ == "__main__":
    unittest.main()
