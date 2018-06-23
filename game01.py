import pygame
import random


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 400


class Element(pygame.sprite.Sprite):
  def __init__(self, color, width, height):
    super().__init__()
    self.image = pygame.Surface([width, height])
    self.image.fill(color)
    self.rect = self.image.get_rect()
    self.delta_x = 0
    self.delta_y = 0

  def get_width(self):
    return self.rect.width

  def get_height(self):
    return self.rect.height

  def get_x(self):
    return self.rect.x

  def get_y(self):
    return self.rect.y

  def set_x(self, x):
    self.rect.x = x

  def set_y(self, y):
    self.rect.y = y

  def set_delta_x(self, delta_x):
    self.delta_x = delta_x

  def set_delta_y(self, delta_y):
    self.delta_y = delta_y

  def update(self):
    self.set_x(self.get_x() + self.delta_x)
    self.set_y(self.get_y() + self.delta_y)


class Block(Element):
  MAX_ENEMY_BULLETS = 5

  def __init__(self):
    super().__init__(RED, width=20, height=15)

  def update(self):
    super().update()
    if self.get_y() > (SCREEN_HEIGHT + 10):
      self.reset_pos()

  def reset_pos(self):
    self.set_x(random.randrange(0, SCREEN_WIDTH))
    self.set_y(random.randrange(-300, -20))

  def fire_at_will(self, player, enemy_bullet_list, all_sprites_list):
    if (len(enemy_bullet_list) >= Block.MAX_ENEMY_BULLETS
        or random.randrange(0, 10000) < 9900):
      return
    bullet = EnemyBullet()
    bullet.set_y(self.get_y() + self.get_height() / 2 - bullet.get_height() / 2)
    if player.get_x() >= self.get_x():
      bullet.set_x(self.get_x() + self.get_width())
      bullet.set_delta_x(2)
    else:
      bullet.set_x(self.get_x() - bullet.get_width())
      bullet.set_delta_x(-2)
    enemy_bullet_list.add(bullet)
    all_sprites_list.add(bullet)


class Player(Element):
  def __init__(self):
    super().__init__(WHITE, width=20, height=15)
    self.score = 0
    self.bullet_timer = 100

  def update(self):
    super().update()
    self.bullet_timer += 1
    if self.get_x() > SCREEN_WIDTH - self.get_width():
      self.set_x(SCREEN_WIDTH - self.get_width())
    elif self.get_x() < 0:
      self.set_x(0)

    if self.get_y() > SCREEN_HEIGHT - self.get_height():
      self.set_y(SCREEN_HEIGHT - self.get_height())
    elif self.get_y() < 0:
      self.set_y(0)

  def fire_bullet(self, player_bullet_list, all_sprites_list):
    if self.bullet_timer < 10 or len(player_bullet_list) >= 10:
      return
    self.bullet_timer = 0
    bullet = PlayerBullet()
    bullet.set_x(self.get_x() + self.get_width() / 2 - bullet.get_width() / 2)
    bullet.set_y(self.get_y() - bullet.get_height())
    player_bullet_list.add(bullet)
    all_sprites_list.add(bullet)


class PlayerBullet(Element):
  def __init__(self):
    super().__init__(WHITE, width=4, height=10)
    self.set_delta_y(-2)


class EnemyBullet(Element):
  def __init__(self):
    super().__init__(RED, width=10, height=4)


class Game(object):
  def __init__(self):
    pygame.init()
    pygame.display.set_caption("My Game")

    self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    self.active_scene = TitleScene()

  def run(self):
    clock = pygame.time.Clock()
    done = False

    while self.active_scene is not None:
      clock.tick(60)
      self.process_input()
      self.update()
      self.draw()
      self.active_scene = self.active_scene.get_next_scene()

    pygame.quit()

  def process_input(self):
    pressed_keys = pygame.key.get_pressed()
    filtered_events = []
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.active_scene.terminate()
        return
      filtered_events.append(event)
    self.active_scene.process_input(filtered_events, pressed_keys)

  def update(self):
    self.active_scene.update()

  def draw(self):
    self.active_scene.draw(self.screen)
    pygame.display.flip()


class SceneBase(object):
  def __init__(self):
    self.next_scene = self

  def process_input(self, events, pressed_keys):
    pass

  def update(self):
    pass

  def draw(self, screen):
    pass

  def switch_to_scene(self, next_scene):
    self.next_scene = next_scene

  def get_next_scene(self):
    return self.next_scene

  def terminate(self):
    self.switch_to_scene(None)


class TitleScene(SceneBase):
  def __init__(self):
    super().__init__()
    self.font = pygame.font.SysFont("monospace", 50, bold=True, italic=False)
    self.text = self.font.render("Press the space key to start.", True, BLUE)

  def process_input(self, events, pressed_keys):
    for event in events:
      if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        self.switch_to_scene(GameScene())

  def draw(self, screen):
    screen.fill(BLACK)
    screen.blit(self.text, [50, 200])


class GameScene(SceneBase):
  NUM_ENEMIES = 10

  def __init__(self):
    super().__init__()
    self.font = pygame.font.SysFont("monospace", 25, bold=True, italic=False)

    self.block_list = pygame.sprite.Group()
    self.player_bullet_list = pygame.sprite.Group()
    self.enemy_bullet_list = pygame.sprite.Group()
    self.all_sprites_list = pygame.sprite.Group()

    for i in range(GameScene.NUM_ENEMIES):
      block = Block()
      block.set_x(random.randrange(SCREEN_WIDTH))
      block.set_y(random.randrange(SCREEN_HEIGHT - 75))
      block.set_delta_y(2)
      self.block_list.add(block)
      self.all_sprites_list.add(block)

    self.player = Player()
    self.player.set_x(SCREEN_WIDTH / 2 - 10)
    self.player.set_y(SCREEN_HEIGHT - 25)
    self.all_sprites_list.add(self.player)

  def process_input(self, events, pressed_keys):
    for event in events:
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
          self.player.set_delta_x(-2)
        elif event.key == pygame.K_RIGHT:
          self.player.set_delta_x(2)
        elif event.key == pygame.K_UP:
          self.player.set_delta_y(-2)
        elif event.key == pygame.K_DOWN:
          self.player.set_delta_y(2)
        elif event.key == pygame.K_SPACE:
          self.player.fire_bullet(self.player_bullet_list, self.all_sprites_list)

      elif event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
          self.player.set_delta_x(0)
        if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
          self.player.set_delta_y(0)

  def update(self):
    for sprite in self.all_sprites_list.sprites():
      sprite.update()

    for bullet in self.player_bullet_list:
      bullet_hit_list = pygame.sprite.spritecollide(bullet, self.block_list, True)
      for block in bullet_hit_list:
        self.player.score += 1
      if bullet_hit_list:
        self.player_bullet_list.remove(bullet)
        self.all_sprites_list.remove(bullet)
      elif bullet.get_y() < -10:
        self.player_bullet_list.remove(bullet)
        self.all_sprites_list.remove(bullet)

    for block in self.block_list:
      block.fire_at_will(self.player, self.enemy_bullet_list, self.all_sprites_list)

    for enemy_bullet in self.enemy_bullet_list:
      if enemy_bullet.get_x() < -10 or enemy_bullet.get_x() > SCREEN_WIDTH:
        self.enemy_bullet_list.remove(enemy_bullet)
        self.all_sprites_list.remove(enemy_bullet)

    block_collide_list = pygame.sprite.spritecollide(self.player, self.block_list, False)
    enemy_bullet_collide_list = pygame.sprite.spritecollide(
        self.player, self.enemy_bullet_list, False)
    if block_collide_list or enemy_bullet_collide_list:
      self.switch_to_scene(LoseScene(self.all_sprites_list))

    if self.player.score >= GameScene.NUM_ENEMIES:
      self.switch_to_scene(WinScene(self.all_sprites_list))

  def draw(self, screen):
    screen.fill(BLACK)
    self.all_sprites_list.draw(screen)
    text = self.font.render("Score: " + str(self.player.score), True, GREEN)
    screen.blit(text, [25, 25])


class WinScene(SceneBase):
  def __init__(self, all_sprites_list):
    super().__init__()
    self.font = pygame.font.SysFont("monospace", 50, bold=True, italic=False)
    self.text = self.font.render("You win!", True, BLUE)
    self.all_sprites_list = all_sprites_list

  def draw(self, screen):
    screen.fill(BLACK)
    self.all_sprites_list.draw(screen)
    screen.blit(self.text, [50, 200])


class LoseScene(SceneBase):
  def __init__(self, all_sprites_list):
    super().__init__()
    self.font = pygame.font.SysFont("monospace", 50, bold=True, italic=False)
    self.text = self.font.render("You lose!", True, RED)
    self.all_sprites_list = all_sprites_list

  def draw(self, screen):
    screen.fill(BLACK)
    self.all_sprites_list.draw(screen)
    screen.blit(self.text, [50, 200])


def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
