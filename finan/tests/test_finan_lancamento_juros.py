# -*- coding: utf-8 -*-
# Copyright 2018 KMEE
# Bruna Braga <bruna.braga@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields
import openerp.tests.common as test_common


class FinanLancamentoReceberManualJuros(test_common.SingleTransactionCase):
    def setUp(self):
        super(FinanLancamentoReceberManualJuros, self).setUp()
        self.finan_lancamento = self.env['finan.lancamento']
        self.finan_lancamento_a_receber = self.finan_lancamento.create({
            'situacao_divida': 'a_vencer',
            'empresa_id': self.env.ref('l10n_br_base.'
                                       'sped_empresa_regime_normal_sp').id,
            'participante_id': self.env.ref('l10n_br_base.cliente9_mg').id,
            'documento_id': self.env.ref('finan.DOCUMENTO_FINANCEIRO_BOLETO').
                            id,
            'numero': 3567,
            'data_documento': fields.Datetime.
                              from_string('2016-03-21 00:00:00'),
            'conta_id': self.env.ref('finan.financial_account_101001').id,
            'data_vencimento': fields.Datetime.
                               from_string('2016-03-21 00:00:00'),
            'forma_pagamento_id': self.env.
                                  ref('finan.finan_forma_pagamento_001').id,
            'banco_id': self.env.ref('finan.finan_banco_237').id,
            'vr_documento': 265.92,
            'tipo': 'a_receber',
            'carteira_id': self.env.ref('finan.finan_carteira_001').id,
        })
        self.finan_lancamento_a_receber.confirma_lancamento()
        self.finan_lancamento_recebimento = self.finan_lancamento.create({
            'empresa_id': self.env.ref('l10n_br_base.'
                                       'sped_empresa_regime_normal_sp').id,
            'documento_id': self.env.ref(
                'finan.DOCUMENTO_FINANCEIRO_BOLETO').id,
            'numero': 3567,
            'data_credito_debito': fields.Datetime.from_string(
                '2016-03-22 00:00:00'),
            'conta_id': self.env.ref('finan.financial_account_101001').id,
            'data_pagamento': fields.Datetime.from_string(
                '2016-03-22 00:00:00'),
            'forma_pagamento_id': self.env.ref(
                'finan.finan_forma_pagamento_001').id,
            'banco_id': self.env.ref('finan.finan_banco_237').id,
            'vr_documento': 265.92,
            'tipo': 'recebimento',
            'vr_movimentado': 265.90,
            'vr_multa': 0,
            'vr_juros': 10.01,
            'vr_adiantado': 0,
            'vr_desconto': 0,
            'vr_tarifas': 0,
        })

    def teste1_lancamento_a_receber_state(self):
        """"
        Teste 1: O state de uma conta a receber deve ser efetivo(open)
        e o provisorio dele, falso
        """
        self.assertEqual(self.finan_lancamento_a_receber.provisorio, False)
        self.assertEqual(self.finan_lancamento_a_receber.state, 'open')

    def teste2_lancamento_recebimento_state(self):
        """"
        Teste 2: O provisorio deve ser falso
        """
        self.assertEqual(self.finan_lancamento_recebimento.provisorio, False)
        self.assertEqual(self.finan_lancamento_recebimento.state, 'paid')

    def teste3_saldo_divida_zerado(self):
        """"
        Teste 3: O saldo após a divida ter recebimento deve ser zerado
        """
        self.finan_lancamento_recebimento.divida_id = self.\
            finan_lancamento_a_receber.id
        self.assertEqual(self.finan_lancamento_a_receber.vr_saldo, 0)

    def teste4_a_receber_state(self):
        """"
        Teste 4: Após o recebimento, a dívida tem quer ter state quitado(paid)
        """
        self.finan_lancamento_recebimento.divida_id = self.\
            finan_lancamento_a_receber.id
        self.assertEqual(self.finan_lancamento_a_receber.state, 'paid')
