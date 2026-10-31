import sys
import pygame

# Inicialização
pygame.init()
pygame.font.init()

# Configurações da Tela
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
SIDEBAR_WIDTH = 300
WIDTH = BOARD_SIZE + SIDEBAR_WIDTH
HEIGHT = BOARD_SIZE

OFFSET_X = 0
OFFSET_Y = 0

# Cores
COLOR_BG = (32, 30, 28)
COLOR_PANEL = (40, 38, 35)
COLOR_LIGHT = (235, 236, 208)
COLOR_DARK = (119, 148, 85)
COLOR_HIGHLIGHT = (246, 246, 105, 180)
COLOR_CHECK = (235, 64, 52, 200)
COLOR_TEXT = (240, 240, 240)
COLOR_RED = (235, 97, 80)
COLOR_BORDER = (60, 58, 55)
COLOR_BTN_ACCENT = (119, 148, 85)

PIECES = {
    'P': '♟', 'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚',  # Pretas
    'p': '♙', 'r': '♖', 'n': '♘', 'b': '♗', 'q': '♕', 'k': '♔'   # Brancas
}

PIECE_NAMES = {
    'P': 'Peão (P)', 'p': 'Peão (B)',
    'R': 'Torre (P)', 'r': 'Torre (B)',
    'N': 'Cavalo (P)', 'n': 'Cavalo (B)',
    'B': 'Bispo (P)', 'b': 'Bispo (B)',
    'Q': 'Rainha (P)', 'q': 'Rainha (B)',
    'K': 'Rei (P)', 'k': 'Rei (B)'
}

class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Xadrez Profissional - 10 Minutos & Reinício Rápido")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Segoe UI Symbol", 54)
        self.ui_font = pygame.font.SysFont("Arial", 12, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 11)
        self.coord_font = pygame.font.SysFont("Arial", 13, bold=True)
        
        self.reset_game()

    def reset_game(self):
        self.board = [
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        ]
        self.turn = 'white'
        self.selected_piece = None
        self.valid_moves = []
        
        self.white_time = 600.0  # 10 minutos
        self.black_time = 600.0  # 10 minutos
        self.move_history = []
        self.captured_by_white = []
        self.captured_by_black = []
        
        self.moved_status = {
            'white_king': False,
            'white_rook_left': False,
            'white_rook_right': False,
            'black_king': False,
            'black_rook_left': False,
            'black_rook_right': False
        }
        
        self.game_over = False
        self.winner_text = ""
        self.board_flipped = False

    def run(self):
        last_time = pygame.time.get_ticks()
        self.running = True
        while self.running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0
            last_time = current_time

            self.handle_events()
            self.update(dt)
            self.render()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                self.handle_click(pos)

    def handle_click(self, pos):
        x, y = pos

        if self.game_over:
            btn_w, btn_h = 240, 45
            btn_rect = pygame.Rect((WIDTH - btn_w) // 2, (HEIGHT // 2) + 30, btn_w, btn_h)
            if btn_rect.collidepoint(pos):
                self.reset_game()
            return

        # Cliques na barra inferior do painel lateral (Empate, Desistir, Reiniciar, Inverter)
        if BOARD_SIZE <= x < WIDTH:
            bar_y = HEIGHT - 45
            if bar_y <= y <= HEIGHT:
                rel_x = x - BOARD_SIZE
                # Dividindo o espaço de 300px para 4 botões: Empate, Desistir, Reiniciar, Inverter
                if rel_x < 75:       # Empate
                    if not self.game_over:
                        self.game_over = True
                        self.winner_text = "Partida encerrada por Empate!"
                elif rel_x < 150:    # Desistir
                    if not self.game_over:
                        self.game_over = True
                        winner = "Pretas" if self.turn == 'white' else "Brancas"
                        self.winner_text = f"Desistência! {winner} venceram!"
                elif rel_x < 225:    # Reiniciar
                    self.reset_game()
                else:                # Inverter Tabuleiro
                    self.board_flipped = not self.board_flipped
                    self.selected_piece = None
                    self.valid_moves = []
                return

        if OFFSET_X <= x < OFFSET_X + BOARD_SIZE and OFFSET_Y <= y < OFFSET_Y + BOARD_SIZE:
            col = (x - OFFSET_X) // SQUARE_SIZE
            row = (y - OFFSET_Y) // SQUARE_SIZE
            
            if self.board_flipped:
                row = 7 - row
                col = 7 - col
            
            piece = self.board[row][col]
            
            if self.selected_piece:
                sel_row, sel_col = self.selected_piece
                if (sel_row, sel_col) == (row, col):
                    self.selected_piece = None
                    self.valid_moves = []
                else:
                    is_roque, rook_start_col, rook_end_col = self.check_castling(sel_row, sel_col, row, col)
                    
                    if is_roque or (row, col) in self.valid_moves:
                        temp_board = [r[:] for r in self.board]
                        
                        if is_roque:
                            temp_board[row][col] = temp_board[sel_row][sel_col]
                            temp_board[sel_row][sel_col] = '.'
                            temp_board[row][rook_end_col] = temp_board[row][rook_start_col]
                            temp_board[row][rook_start_col] = '.'
                        else:
                            temp_board[row][col] = temp_board[sel_row][sel_col]
                            temp_board[sel_row][sel_col] = '.'
                        
                        color_to_check = 'white' if self.turn == 'white' else 'black'
                        if self.is_in_check(temp_board, color_to_check):
                            self.selected_piece = None
                            self.valid_moves = []
                            return

                        target_piece = self.board[row][col]
                        if target_piece != '.':
                            if self.turn == 'white':
                                self.captured_by_white.append(target_piece)
                            else:
                                self.captured_by_black.append(target_piece)

                        if is_roque:
                            self.board[row][col] = self.board[sel_row][sel_col]
                            self.board[sel_row][sel_col] = '.'
                            self.board[row][rook_end_col] = self.board[row][rook_start_col]
                            self.board[row][rook_start_col] = '.'
                            
                            if self.turn == 'white':
                                self.moved_status['white_king'] = True
                            else:
                                self.moved_status['black_king'] = True
                        else:
                            moved_piece = self.board[sel_row][sel_col]
                            
                            if moved_piece == 'k': self.moved_status['white_king'] = True
                            elif moved_piece == 'K': self.moved_status['black_king'] = True
                            elif moved_piece == 'r' and sel_row == 7 and sel_col == 0: self.moved_status['white_rook_left'] = True
                            elif moved_piece == 'r' and sel_row == 7 and sel_col == 7: self.moved_status['white_rook_right'] = True
                            elif moved_piece == 'R' and sel_row == 0 and sel_col == 0: self.moved_status['black_rook_left'] = True
                            elif moved_piece == 'R' and sel_row == 0 and sel_col == 7: self.moved_status['black_rook_right'] = True

                            origin_str = f"{['a','b','c','d','e','f','g','h'][sel_col]}{8-sel_row}"
                            dest_str = f"{['a','b','c','d','e','f','g','h'][col]}{8-row}"
                            
                            self.move_history.append({
                                'piece': moved_piece,
                                'from': origin_str,
                                'to': dest_str
                            })

                            self.board[row][col] = self.board[sel_row][sel_col]
                            self.board[sel_row][sel_col] = '.'

                        self.turn = 'black' if self.turn == 'white' else 'white'
                        
                        next_color = 'white' if self.turn == 'white' else 'black'
                        if self.is_checkmate(next_color):
                            self.game_over = True
                            winner_name = "Brancas" if self.turn == 'white' else "Pretas"
                            self.winner_text = f"Xeque-Mate! {winner_name} venceram!"

                    self.selected_piece = None
                    self.valid_moves = []
            else:
                if piece != '.':
                    if self.turn == 'white' and piece.islower():
                        self.selected_piece = (row, col)
                        self.calculate_valid_moves(row, col)
                    elif self.turn == 'black' and piece.isupper():
                        self.selected_piece = (row, col)
                        self.calculate_valid_moves(row, col)

    def calculate_valid_moves(self, start_r, start_c):
        self.valid_moves = []
        color = 'white' if self.turn == 'white' else 'black'
        for r in range(8):
            for c in range(8):
                if self.is_valid_move(self.board, start_r, start_c, r, c):
                    temp_board = [row[:] for row in self.board]
                    temp_board[r][c] = temp_board[start_r][start_c]
                    temp_board[start_r][start_c] = '.'
                    if not self.is_in_check(temp_board, color):
                        self.valid_moves.append((r, c))

    def check_castling(self, start_r, start_c, end_r, end_c):
        piece = self.board[start_r][start_c]
        if piece == 'k' and start_r == 7 and start_c == 4:
            if not self.moved_status['white_king'] and not self.is_in_check(self.board, 'white'):
                if end_r == 7 and end_c == 6 and not self.moved_status['white_rook_right']:
                    if self.board[7][5] == '.' and self.board[7][6] == '.':
                        return True, 7, 5
                if end_r == 7 and end_c == 2 and not self.moved_status['white_rook_left']:
                    if self.board[7][1] == '.' and self.board[7][2] == '.' and self.board[7][3] == '.':
                        return True, 0, 3
        
        elif piece == 'K' and start_r == 0 and start_c == 4:
            if not self.moved_status['black_king'] and not self.is_in_check(self.board, 'black'):
                if end_r == 0 and end_c == 6 and not self.moved_status['black_rook_right']:
                    if self.board[0][5] == '.' and self.board[0][6] == '.':
                        return True, 7, 5
                if end_r == 0 and end_c == 2 and not self.moved_status['black_rook_left']:
                    if self.board[0][1] == '.' and self.board[0][2] == '.' and self.board[0][3] == '.':
                        return True, 0, 3
        return False, 0, 0

    def is_valid_move(self, board, start_r, start_c, end_r, end_c):
        piece = board[start_r][start_c]
        target = board[end_r][end_c]
        
        if target != '.':
            if piece.islower() and target.islower(): return False
            if piece.isupper() and target.isupper(): return False

        p_lower = piece.lower()
        
        if p_lower == 'p':
            direction = -1 if piece.islower() else 1
            start_row = 6 if piece.islower() else 1
            
            if start_c == end_c and target == '.':
                if end_r == start_r + direction: return True
                if start_r == start_row and end_r == start_r + (2 * direction) and board[start_r + direction][start_c] == '.': return True
            if abs(start_c - end_c) == 1 and end_r == start_r + direction and target != '.': return True
            return False

        elif p_lower == 'r':
            if start_r != end_r and start_c != end_c: return False
            return self.is_path_clear(board, start_r, start_c, end_r, end_c)

        elif p_lower == 'b':
            if abs(start_r - end_r) != abs(start_c - end_c): return False
            return self.is_path_clear(board, start_r, start_c, end_r, end_c)

        elif p_lower == 'q':
            if start_r != end_r and start_c != end_c and abs(start_r - end_r) != abs(start_c - end_c): return False
            return self.is_path_clear(board, start_r, start_c, end_r, end_c)

        elif p_lower == 'k':
            if max(abs(start_r - end_r), abs(start_c - end_c)) == 1: return True
            return False

        elif p_lower == 'n':
            dr = abs(start_r - end_r)
            dc = abs(start_c - end_c)
            if (dr == 2 and dc == 1) or (dr == 1 and dc == 2): return True
            return False

        return False

    def is_path_clear(self, board, start_r, start_c, end_r, end_c):
        step_r = 0 if start_r == end_r else (1 if end_r > start_r else -1)
        step_c = 0 if start_c == end_c else (1 if end_c > start_c else -1)
        
        curr_r, curr_c = start_r + step_r, start_c + step_c
        while curr_r != end_r or curr_c != end_c:
            if board[curr_r][curr_c] != '.': return False
            curr_r += step_r
            curr_c += step_c
        return True

    def find_king(self, board, color):
        target_king = 'k' if color == 'white' else 'K'
        for r in range(8):
            for c in range(8):
                if board[r][c] == target_king:
                    return (r, c)
        return None

    def is_in_check(self, board, color):
        king_pos = self.find_king(board, color)
        if not king_pos: return False
        kr, kc = king_pos

        opponent_color_is_upper = (color == 'white')
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece != '.':
                    is_upper = piece.isupper()
                    if is_upper == opponent_color_is_upper:
                        if self.is_valid_move(board, r, c, kr, kc):
                            return True
        return False

    def is_checkmate(self, color):
        if not self.is_in_check(self.board, color):
            return False

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != '.' and ((color == 'white' and piece.islower()) or (color == 'black' and piece.isupper())):
                    for tr in range(8):
                        for tc in range(8):
                            if self.is_valid_move(self.board, r, c, tr, tc):
                                temp_board = [row[:] for row in self.board]
                                temp_board[tr][tc] = temp_board[r][c]
                                temp_board[r][c] = '.'
                                if not self.is_in_check(temp_board, color):
                                    return False
        return True

    def update(self, dt):
        if self.game_over:
            return

        if self.turn == 'white':
            self.white_time -= dt
            if self.white_time <= 0:
                self.white_time = 0
                self.game_over = True
                self.winner_text = "Tempo esgotado! Pretas venceram!"
        else:
            self.black_time -= dt
            if self.black_time <= 0:
                self.black_time = 0
                self.game_over = True
                self.winner_text = "Tempo esgotado! Brancas venceram!"

    def render(self):
        self.screen.fill(COLOR_BG)
        
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['8', '7', '6', '5', '4', '3', '2', '1']

        if self.board_flipped:
            files = files[::-1]
            ranks = ranks[::-1]

        current_color = 'white' if self.turn == 'white' else 'black'
        king_in_check = self.is_in_check(self.board, current_color)
        king_pos = self.find_king(self.board, current_color) if king_in_check else None

        for r in range(8):
            for c in range(8):
                board_r = 7 - r if self.board_flipped else r
                board_c = 7 - c if self.board_flipped else c

                color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
                rect = pygame.Rect(OFFSET_X + c * SQUARE_SIZE, OFFSET_Y + r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                
                if king_pos and (board_r, board_c) == king_pos:
                    check_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    check_surf.fill(COLOR_CHECK)
                    self.screen.blit(check_surf, rect.topleft)
                elif self.selected_piece == (board_r, board_c):
                    highlight_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    highlight_surf.fill(COLOR_HIGHLIGHT)
                    self.screen.blit(highlight_surf, rect.topleft)

                if (board_r, board_c) in self.valid_moves:
                    indicator_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    if self.board[board_r][board_c] == '.':
                        pygame.draw.circle(indicator_surf, (0, 0, 0, 80), (SQUARE_SIZE // 2, SQUARE_SIZE // 2), 12)
                    else:
                        pygame.draw.rect(indicator_surf, (0, 0, 0, 100), indicator_surf.get_rect(), 6)
                    self.screen.blit(indicator_surf, rect.topleft)

                if c == 0:
                    rank_surf = self.coord_font.render(ranks[r], True, COLOR_TEXT if (r+c)%2==0 else COLOR_LIGHT)
                    self.screen.blit(rank_surf, (OFFSET_X + 4, OFFSET_Y + r * SQUARE_SIZE + 4))
                if r == 7:
                    file_surf = self.coord_font.render(files[c], True, COLOR_TEXT if (r+c)%2==0 else COLOR_LIGHT)
                    self.screen.blit(file_surf, (OFFSET_X + c * SQUARE_SIZE + SQUARE_SIZE - 14, OFFSET_Y + BOARD_SIZE - 16))

                piece = self.board[board_r][board_c]
                if piece != '.':
                    p_color = (0, 0, 0) if piece.isupper() else (255, 255, 255)
                    text_surf = self.font.render(PIECES[piece], True, p_color)
                    text_rect = text_surf.get_rect(center=rect.center)
                    self.screen.blit(text_surf, text_rect)

        # Painel Lateral
        sidebar_rect = pygame.Rect(BOARD_SIZE, 0, SIDEBAR_WIDTH, HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL, sidebar_rect)
        pygame.draw.line(self.screen, COLOR_BORDER, (BOARD_SIZE, 0), (BOARD_SIZE, HEIGHT), 2)

        bw_min, bw_sec = divmod(int(self.black_time), 60)
        ww_min, ww_sec = divmod(int(self.white_time), 60)
        
        b_txt = self.ui_font.render(f"Pretas: {bw_min:02d}:{bw_sec:02d}", True, COLOR_RED if self.turn == 'black' else COLOR_TEXT)
        w_txt = self.ui_font.render(f"Brancas: {ww_min:02d}:{ww_sec:02d}", True, COLOR_RED if self.turn == 'white' else COLOR_TEXT)
        
        self.screen.blit(b_txt, (BOARD_SIZE + 15, 10))
        self.screen.blit(w_txt, (BOARD_SIZE + 15, HEIGHT - 85))

        cap_b_str = "Comidas (P): " + "".join([PIECES[p] for p in self.captured_by_white])
        cap_w_str = "Comidas (B): " + "".join([PIECES[p] for p in self.captured_by_black])
        
        cap_b_surf = self.small_font.render(cap_b_str, True, (200, 200, 200))
        cap_w_surf = self.small_font.render(cap_w_str, True, (200, 200, 200))
        
        self.screen.blit(cap_b_surf, (BOARD_SIZE + 15, 32))
        self.screen.blit(cap_w_surf, (BOARD_SIZE + 15, HEIGHT - 65))

        title_surf = self.ui_font.render("Histórico de Movimentos", True, COLOR_TEXT)
        self.screen.blit(title_surf, (BOARD_SIZE + 15, 55))
        
        header_surf = self.small_font.render("Peça          Origem  ->  Destino", True, (180, 180, 180))
        self.screen.blit(header_surf, (BOARD_SIZE + 15, 75))
        pygame.draw.line(self.screen, COLOR_BORDER, (BOARD_SIZE + 15, 92), (WIDTH - 15, 92), 1)

        start_y = 100
        max_display = 18
        visible_moves = self.move_history[-max_display:]
        
        for i, move in enumerate(visible_moves):
            p_name = PIECE_NAMES.get(move['piece'], 'Peça')
            text_line = f"{p_name:<11}   {move['from']}     ->     {move['to']}"
            line_surf = self.small_font.render(text_line, True, COLOR_TEXT)
            self.screen.blit(line_surf, (BOARD_SIZE + 15, start_y + (i * 18)))

        # --- BARRA INFERIOR ESTILO CHESS.COM (Empate, Desistir, Reiniciar, Inverter) ---
        bar_y = HEIGHT - 45
        pygame.draw.line(self.screen, COLOR_BORDER, (BOARD_SIZE, bar_y), (WIDTH, bar_y), 1)
        
        empate_surf = self.ui_font.render("½ Empate", True, COLOR_TEXT)
        self.screen.blit(empate_surf, (BOARD_SIZE + 12, bar_y + 13))

        desistir_surf = self.ui_font.render("⚑ Desistir", True, COLOR_TEXT)
        self.screen.blit(desistir_surf, (BOARD_SIZE + 80, bar_y + 13))

        reiniciar_surf = self.ui_font.render("↻ Reiniciar", True, COLOR_TEXT)
        self.screen.blit(reiniciar_surf, (BOARD_SIZE + 150, bar_y + 13))

        invert_surf = self.ui_font.render("⇄", True, COLOR_TEXT)
        self.screen.blit(invert_surf, (WIDTH - 30, bar_y + 10))

        # Tela de Fim de Jogo com Botão de Continuar do Zero
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 210))
            self.screen.blit(overlay, (0, 0))
            
            end_txt = self.ui_font.render(self.winner_text, True, (255, 255, 0))
            end_rect = end_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            self.screen.blit(end_txt, end_rect)

            btn_w, btn_h = 240, 45
            btn_rect = pygame.Rect((WIDTH - btn_w) // 2, (HEIGHT // 2) + 20, btn_w, btn_h)
            pygame.draw.rect(self.screen, COLOR_BTN_ACCENT, btn_rect, border_radius=6)
            
            cont_txt = self.ui_font.render("Continuar do Zero", True, COLOR_TEXT)
            self.screen.blit(cont_txt, cont_txt.get_rect(center=btn_rect.center))

        pygame.display.flip()

if __name__ == "__main__":
    game = ChessGame()
    game.run()