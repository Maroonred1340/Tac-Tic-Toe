import random
from enum import Enum
from typing import List, Tuple, Optional, Set, Dict
from dataclasses import dataclass, field
import copy

class VictoryType(Enum):
    """승리 조건 타입"""
    HORIZONTAL_4 = "horizontal_4"  # 가로 4칸
    VERTICAL_4 = "vertical_4"  # 세로 4칸
    DIAGONAL_4 = "diagonal_4"  # 대각선 4칸
    SQUARE_2X2 = "square_2x2"  # 2x2 정사각형
    L_SHAPE = "l_shape"  # ㄱ자 모양
    CROSS = "cross"  # 십자가
    CORNER_4 = "corner_4"  # 모서리 4칸
    CENTER_4 = "center_4"  # 중앙 4칸
    KNIGHT_3 = "knight_3"  # 체스 나이트 3칸
    QUEEN_3 = "queen_3"  # 체스 퀸 3칸
    EVEN_CELLS = "even_cells"  # 짝수 칸만
    ODD_CELLS = "odd_cells"  # 홀수 칸만
    SYMMETRY = "symmetry"  # 대칭 구조
    ALL_EDGES = "all_edges"  # 모든 변
    CLASSIC = "classic"  # 기본 3칸
    SPIRAL = "spiral"  # 나선형
    STAR = "star"  # 별 모양

class TurnType(Enum):
    """턴 규칙 타입"""
    NORMAL = "normal"  # 일반 1칸
    DOUBLE_PLACE = "double_place"  # 2칸 놓기
    FLIP_OPPONENT = "flip_opponent"  # 상대 돌 뒤집기
    MOVE_STONE = "move_stone"  # 돌 이동
    SEAL_RANDOM = "seal_random"  # 랜덤 칸 봉인
    DICE_ROLL = "dice_roll"  # 주사위로 위치 결정

class SpecialCellType(Enum):
    """특수 칸 타입"""
    DOUBLE_SCORE = "double_score"  # 점수 2배
    DISAPPEAR = "disappear"  # 돌이 사라짐
    REMOVE_OPPONENT = "remove_opponent"  # 상대 돌 제거
    ONE_TIME = "one_time"  # 한 번만 사용
    SHARED = "shared"  # 양쪽 모두 차지 가능

class PowerType(Enum):
    """특수 능력 타입"""
    REMOVE_OPPONENT = "remove_opponent"  # 상대 돌 제거
    DOUBLE_PLACE = "double_place"  # 돌 2개 놓기
    SWAP_POSITION = "swap_position"  # 위치 바꾸기
    SKIP_OPPONENT = "skip_opponent"  # 상대 턴 스킵
    NEGATE = "negate"  # 무효화

@dataclass
class GameRules:
    """게임 규칙 설정"""
    victory_type: VictoryType
    turn_type: TurnType
    special_cells: Dict[Tuple[int, int], SpecialCellType] = field(default_factory=dict)
    scoring_mode: bool = False
    score_target: int = 5
    powers_enabled: bool = True

class TacTicToe:
    """택틱토 게임"""
    
    def __init__(self):
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.sealed_cells: Set[Tuple[int, int]] = set()
        self.used_one_time_cells: Set[Tuple[int, int]] = set()
        self.rules: Optional[GameRules] = None
        self.player_score = 0
        self.ai_score = 0
        self.player_powers: Dict[PowerType, int] = {
            PowerType.REMOVE_OPPONENT: 1,
            PowerType.DOUBLE_PLACE: 1,
            PowerType.SWAP_POSITION: 1,
            PowerType.SKIP_OPPONENT: 1,
            PowerType.NEGATE: 1,
        }
        self.ai_powers: Dict[PowerType, int] = {
            PowerType.REMOVE_OPPONENT: 1,
            PowerType.DOUBLE_PLACE: 1,
            PowerType.SWAP_POSITION: 1,
            PowerType.SKIP_OPPONENT: 1,
            PowerType.NEGATE: 1,
        }
        self.last_move = None
        self.skip_next_turn = False

    def randomize_rules(self):
        """랜덤하게 게임 규칙 선택"""
        victory_type = random.choice(list(VictoryType))
        turn_type = random.choice(list(TurnType))
        
        # 특수 칸 30% 확률로 추가
        special_cells = {}
        if random.random() < 0.3:
            num_special = random.randint(1, 3)
            positions = [(i, j) for i in range(3) for j in range(3)]
            random.shuffle(positions)
            for pos in positions[:num_special]:
                special_cells[pos] = random.choice(list(SpecialCellType))
        
        # 점수제 규칙 30% 확률
        scoring_mode = random.random() < 0.3
        
        self.rules = GameRules(
            victory_type=victory_type,
            turn_type=turn_type,
            special_cells=special_cells,
            scoring_mode=scoring_mode,
            powers_enabled=True
        )
        
        return self.rules

    def display_board(self):
        """게임판 표시"""
        print("\n  0 1 2")
        for i in range(3):
            row = f"{i} "
            for j in range(3):
                cell = self.board[i][j]
                if (i, j) in self.sealed_cells:
                    row += "# "
                elif cell == 'O':
                    row += "O "
                elif cell == 'X':
                    row += "X "
                else:
                    row += ". "
            print(row)
        
        # 마지막 수 표시
        if self.last_move:
            print(f"\n📍 마지막 수: {self.last_move}")
        print()

    def is_valid_move(self, row: int, col: int) -> bool:
        """유효한 이동인지 확인"""
        if not (0 <= row < 3 and 0 <= col < 3):
            return False
        if (row, col) in self.sealed_cells:
            return False
        if (row, col) in self.used_one_time_cells:
            return False
        
        special_cell_type = self.rules.special_cells.get((row, col))
        if special_cell_type == SpecialCellType.SHARED:
            return True
        
        return self.board[row][col] is None

    def place_stone(self, row: int, col: int, player: str) -> bool:
        """돌 놓기"""
        if not self.is_valid_move(row, col):
            return False
        
        special_cell_type = self.rules.special_cells.get((row, col))
        
        # 특수 칸 처리
        if special_cell_type == SpecialCellType.ONE_TIME:
            self.used_one_time_cells.add((row, col))
        elif special_cell_type == SpecialCellType.DISAPPEAR:
            return True  # 돌이 나타나지 않음
        
        self.board[row][col] = player
        self.last_move = (row, col)
        return True

    def check_horizontal_4(self, player: str) -> bool:
        """가로 4칸 확인 (3x3에서는 불가능하므로 3칸으로 변경)"""
        for i in range(3):
            for j in range(1):  # 0, 1 위치에서만 체크
                if (j + 2 < 3 and 
                    self.board[i][j] == player and 
                    self.board[i][j+1] == player and 
                    self.board[i][j+2] == player):
                    return True
        return False

    def check_vertical_4(self, player: str) -> bool:
        """세로 4칸 확인 (3칸으로 변경)"""
        for j in range(3):
            for i in range(1):
                if (i + 2 < 3 and
                    self.board[i][j] == player and 
                    self.board[i+1][j] == player and 
                    self.board[i+2][j] == player):
                    return True
        return False

    def check_diagonal_4(self, player: str) -> bool:
        """대각선 4칸 확인 (3칸으로 변경)"""
        # 좌상향 대각선
        if (self.board[0][0] == player and 
            self.board[1][1] == player and 
            self.board[2][2] == player):
            return True
        # 우상향 대각선
        if (self.board[0][2] == player and 
            self.board[1][1] == player and 
            self.board[2][0] == player):
            return True
        return False

    def check_square_2x2(self, player: str) -> bool:
        """2x2 정사각형 확인"""
        for i in range(2):
            for j in range(2):
                if (self.board[i][j] == player and
                    self.board[i][j+1] == player and
                    self.board[i+1][j] == player and
                    self.board[i+1][j+1] == player):
                    return True
        return False

    def check_l_shape(self, player: str) -> bool:
        """ㄱ자 모양 확인"""
        l_patterns = [
            [(0,0), (1,0), (2,0), (2,1)],  # └
            [(0,0), (0,1), (0,2), (1,2)],  # ⌐
            [(0,2), (1,2), (2,2), (2,1)],  # ┘
            [(0,0), (0,1), (0,2), (1,0)],  # ⌞
        ]
        for pattern in l_patterns:
            if all(self.board[r][c] == player for r, c in pattern):
                return True
        return False

    def check_cross(self, player: str) -> bool:
        """십자가 모양 확인"""
        cross_pattern = [(0,1), (1,0), (1,1), (1,2), (2,1)]
        if all(self.board[r][c] == player for r, c in cross_pattern):
            return True
        return False

    def check_corner_4(self, player: str) -> bool:
        """모서리 4칸 확인"""
        corners = [(0,0), (0,2), (2,0), (2,2)]
        if all(self.board[r][c] == player for r, c in corners):
            return True
        return False

    def check_center_4(self, player: str) -> bool:
        """중앙 4칸 확인"""
        center = [(0,1), (1,0), (1,2), (2,1)]
        if all(self.board[r][c] == player for r, c in center):
            return True
        return False

    def check_knight_3(self, player: str) -> bool:
        """체스 나이트 패턴 3칸 확인"""
        knight_moves = [
            [(0,0), (1,2), (2,1)],
            [(0,1), (2,0), (2,2)],
            [(0,2), (1,0), (2,1)],
            [(1,0), (0,2), (2,2)],
        ]
        for pattern in knight_moves:
            if all(self.board[r][c] == player for r, c in pattern):
                return True
        return False

    def check_queen_3(self, player: str) -> bool:
        """체스 퀸 패턴 3칸 확인"""
        queen_patterns = [
            [(0,0), (1,1), (2,2)],  # 대각선
            [(0,2), (1,1), (2,0)],  # 대각선
            [(0,1), (1,1), (2,1)],  # 세로
            [(1,0), (1,1), (1,2)],  # 가로
        ]
        for pattern in queen_patterns:
            if all(self.board[r][c] == player for r, c in pattern):
                return True
        return False

    def check_even_cells(self, player: str) -> bool:
        """짝수 칸만 점령 확인"""
        even_count = 0
        total_even = 0
        for i in range(3):
            for j in range(3):
                if (i + j) % 2 == 0:
                    total_even += 1
                    if self.board[i][j] == player:
                        even_count += 1
        return even_count == total_even and total_even > 0

    def check_odd_cells(self, player: str) -> bool:
        """홀수 칸만 점령 확인"""
        odd_count = 0
        total_odd = 0
        for i in range(3):
            for j in range(3):
                if (i + j) % 2 == 1:
                    total_odd += 1
                    if self.board[i][j] == player:
                        odd_count += 1
        return odd_count == total_odd and total_odd > 0

    def check_symmetry(self, player: str) -> bool:
        """대칭 구조 완성 확인"""
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == player:
                    if self.board[2-i][2-j] != player:
                        return False
        return any(self.board[i][j] == player for i in range(3) for j in range(3))

    def check_all_edges(self, player: str) -> bool:
        """모든 변을 차지 확인"""
        edges = [
            (0,0), (0,1), (0,2),  # 상단
            (1,0), (1,2),  # 좌우
            (2,0), (2,1), (2,2),  # 하단
        ]
        return all(self.board[r][c] == player for r, c in edges)

    def check_spiral(self, player: str) -> bool:
        """나선형 패턴 확인"""
        spiral_patterns = [
            [(0,0), (0,1), (1,1), (2,1), (2,0)],
            [(0,2), (1,2), (1,1), (1,0), (0,0)],
            [(2,2), (2,1), (1,1), (0,1), (0,2)],
        ]
        for pattern in spiral_patterns:
            if all(self.board[r][c] == player for r, c in pattern):
                return True
        return False

    def check_star(self, player: str) -> bool:
        """별 모양 패턴 확인"""
        star_patterns = [
            [(0,1), (1,0), (1,1), (1,2), (2,1)],
            [(0,0), (0,1), (1,1), (2,0), (2,1)],
            [(0,1), (0,2), (1,1), (2,1), (2,2)],
        ]
        for pattern in star_patterns:
            if all(self.board[r][c] == player for r, c in pattern):
                return True
        return False

    def check_classic_win(self, player: str) -> bool:
        """기본 3칸 승리 확인"""
        return (self.check_horizontal_4(player) or
                self.check_vertical_4(player) or
                self.check_diagonal_4(player))

    def check_win(self, player: str) -> bool:
        """현재 규칙에 따른 승리 확인"""
        if self.rules is None:
            return self.check_classic_win(player)
        
        victory_checks = {
            VictoryType.HORIZONTAL_4: self.check_horizontal_4,
            VictoryType.VERTICAL_4: self.check_vertical_4,
            VictoryType.DIAGONAL_4: self.check_diagonal_4,
            VictoryType.SQUARE_2X2: self.check_square_2x2,
            VictoryType.L_SHAPE: self.check_l_shape,
            VictoryType.CROSS: self.check_cross,
            VictoryType.CORNER_4: self.check_corner_4,
            VictoryType.CENTER_4: self.check_center_4,
            VictoryType.KNIGHT_3: self.check_knight_3,
            VictoryType.QUEEN_3: self.check_queen_3,
            VictoryType.EVEN_CELLS: self.check_even_cells,
            VictoryType.ODD_CELLS: self.check_odd_cells,
            VictoryType.SYMMETRY: self.check_symmetry,
            VictoryType.ALL_EDGES: self.check_all_edges,
            VictoryType.CLASSIC: self.check_classic_win,
            VictoryType.SPIRAL: self.check_spiral,
            VictoryType.STAR: self.check_star,
        }
        
        check_func = victory_checks.get(self.rules.victory_type, self.check_classic_win)
        return check_func(player)

    def is_board_full(self) -> bool:
        """게임판이 가득 찼는지 확인"""
        for row in self.board:
            if None in row:
                return False
        return True

    def get_available_moves(self) -> List[Tuple[int, int]]:
        """사용 가능한 이동 목록"""
        moves = []
        for i in range(3):
            for j in range(3):
                if self.is_valid_move(i, j):
                    moves.append((i, j))
        return moves

    def ai_move(self) -> Optional[Tuple[int, int]]:
        """AI의 움직임 결정"""
        available = self.get_available_moves()
        
        if not available:
            return None
        
        # 우선순위: 승리 > 상대 차단 > 특수 칸 > 랜덤
        
        # 1. AI가 이길 수 있는 자리 찾기
        for move in available:
            self.board[move[0]][move[1]] = 'X'
            if self.check_win('X'):
                self.board[move[0]][move[1]] = None
                return move
            self.board[move[0]][move[1]] = None
        
        # 2. 플레이어가 이길 수 있는 자리 차단
        for move in available:
            self.board[move[0]][move[1]] = 'O'
            if self.check_win('O'):
                self.board[move[0]][move[1]] = None
                return move
            self.board[move[0]][move[1]] = None
        
        # 3. 특수 칸 우선
        special_moves = [m for m in available if m in self.rules.special_cells]
        if special_moves:
            return random.choice(special_moves)
        
        # 4. 중앙 칸 선호
        center_moves = [m for m in available if m == (1, 1)]
        if center_moves:
            return center_moves[0]
        
        # 5. 랜덤
        return random.choice(available)

    def apply_turn_rule(self, player: str) -> bool:
        """턴 규칙 적용"""
        if self.rules.turn_type == TurnType.SEAL_RANDOM:
            available = self.get_available_moves()
            if available:
                sealed = random.choice(available)
                self.sealed_cells.add(sealed)
                print(f"  🔒 칸 {sealed}이 봉인되었습니다!")
        
        elif self.rules.turn_type == TurnType.DICE_ROLL:
            dice = random.randint(1, 6)
            print(f"  🎲 주사위 결과: {dice}")
        
        return True

    def play_game(self):
        """게임 플레이"""
        print("=" * 40)
        print("  🎮 택틱토 게임 시작! 🎮")
        print("=" * 40)
        
        # 규칙 랜덤화
        rules = self.randomize_rules()
        print(f"\n📋 이번 게임 규칙:")
        print(f"  승리 조건: {rules.victory_type.value}")
        print(f"  턴 규칙: {rules.turn_type.value}")
        if rules.special_cells:
            print(f"  특수 칸: {rules.special_cells}")
        if rules.scoring_mode:
            print(f"  점수제 (목표: {rules.score_target}점)")
        print()
        
        turn = 0
        max_turns = 20
        
        while turn < max_turns:
            self.display_board()
            
            if turn % 2 == 0:  # 플레이어 턴
                print(f"🔵 당신의 턴 (O)")
                print(f"  점수: {self.player_score} | AI 점수: {self.ai_score}")
                
                while True:
                    try:
                        move_input = input("  이동 입력 (행,열) 또는 'q'(종료): ").strip()
                        if move_input.lower() == 'q':
                            print("  게임 종료!")
                            return
                        
                        row, col = map(int, move_input.split(','))
                        
                        if self.place_stone(row, col, 'O'):
                            break
                        else:
                            print("  ❌ 유효하지 않은 이동입니다!")
                    except:
                        print("  ❌ 잘못된 입력입니다!")
                
                if self.check_win('O'):
                    self.display_board()
                    print("🎉 축하합니다! 당신이 이겼습니다!")
                    return
                
            else:  # AI 턴
                print(f"🤖 AI의 턴 (X)")
                move = self.ai_move()
                
                if move:
                    self.place_stone(move[0], move[1], 'X')
                    print(f"  AI가 {move}에 돌을 놓았습니다.")
                
                if self.check_win('X'):
                    self.display_board()
                    print("💔 AI가 승리했습니다!")
                    return
            
            self.apply_turn_rule('O' if turn % 2 == 0 else 'X')
            
            if self.is_board_full():
                self.display_board()
                print("🤝 무승부입니다!")
                return
            
            turn += 1
        
        print("⏱️  턴 제한 도달!")

def main():
    """메인 함수"""
    game = TacTicToe()
    game.play_game()
    
    while True:
        again = input("\n다시 플레이하시겠습니까? (y/n): ").strip().lower()
        if again == 'y':
            game = TacTicToe()
            game.play_game()
        else:
            print("게임을 종료합니다!")
            break

if __name__ == "__main__":
    main()
