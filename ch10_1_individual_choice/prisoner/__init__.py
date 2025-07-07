from otree.api import *


doc = """
This is a one-shot "Prisoner's Dilemma". Two players are asked separately
whether they want to cooperate or defect. Their choices directly determine the
payoffs.
"""


class C(BaseConstants):
    NAME_IN_URL = 'prisoner'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 2
    PAYOFF_A = cu(400)
    PAYOFF_B = cu(200)
    PAYOFF_C = cu(100)
    PAYOFF_D = cu(0)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    cooperate = models.BooleanField(
        choices=[[True, '協力する'], [False, '裏切る']],
        doc="""This player's decision""",
        widget=widgets.RadioSelect,
    )


# FUNCTIONS
def set_payoffs(group: Group):
    for p in group.get_players():
        set_payoff(p)


def other_player(player: Player):
    return player.get_others_in_group()[0]


def set_payoff(player: Player):
    payoff_matrix = {
        (False, True): C.PAYOFF_A,
        (True, True): C.PAYOFF_B,
        (False, False): C.PAYOFF_C,
        (True, False): C.PAYOFF_D,
    }
    other = other_player(player)
    player.payoff = payoff_matrix[(player.cooperate, other.cooperate)]


# PAGES
class Introduction(Page):

    @staticmethod
    def is_displayed(player):
       return player.round_number == 1


class Decision(Page):
    form_model = 'player'
    form_fields = ['cooperate']

    @staticmethod
    def get_timeout_seconds(player):
        # ラウンド2なら60秒、それ以外は制限なし
        return 120 if player.round_number == 2 else None

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.round_number == 2 and timeout_happened:
            # タイムアウト時に自動選択を行う例
            player.cooperate = False


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        opponent = other_player(player)
        return dict(
            opponent=opponent,
            same_choice=player.cooperate == opponent.cooperate,
            my_decision=player.field_display('cooperate'),
            opponent_decision=opponent.field_display('cooperate'),
        )

class Round2Instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 2

    @staticmethod
    def vars_for_template(player):
        return {
            'message': 'ラウンド2では、相手とチャットを通じてコミュニケーションを取ることができます。<br>'
                       'ゲームの基本構造はラウンド1と同じです。<br>'
                       '制限時間が設けられているので注意してください。'
        }

class FinalResults(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS  # 最終ラウンドだけ表示

    @staticmethod
    def vars_for_template(player):
        # participant.payoff はすでに累計得点が入っている
        total = player.participant.payoff
        return {
            'total_payoff': total,
        }


page_sequence = [
    Introduction,
    Round2Instructions,
    Decision,
    ResultsWaitPage,
    Results,
    FinalResults,
]

