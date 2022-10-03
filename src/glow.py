from src.consts import *
from pathlib import Path

class Glow:
    def __init__(self, ctx: arcade.gl.Context):
        self.ctx = ctx
        self.gen_fbs((1280, 720))
        self.screen_quad = arcade.gl.geometry.quad_2d_fs()
        self.program = ctx.program(
            vertex_shader=Path('assets/shaders/glow.vs').read_text(),
            fragment_shader=Path('assets/shaders/glow.fs').read_text()
        )
        size = (1280, 720)
        self.fb_cur = self.ctx.framebuffer(color_attachments=[self.ctx.texture(size, wrap_x=False, wrap_y=False)])
        self.fb_aux = self.ctx.framebuffer(color_attachments=[self.ctx.texture(size, wrap_x=False, wrap_y=False)])
    
    def use(self):
        self.fb.use()

    def gen_fbs(self, size):
        self.fb = self.ctx.framebuffer(color_attachments=[self.ctx.texture(size)])
        
    
    def render(self, target, passes=3):
        flip = False
        self.program["tex"] = 0
        self.program["tex2"] = 1
        self.program["blend"] = False
        for i in range(passes*2-1):
            self.program["flip"] = flip
            self.fb_aux.use()
            if i == 0:
                self.fb.color_attachments[0].use(0)
            else:
                self.fb_cur.color_attachments[0].use(0)
            self.fb_aux, self.fb_cur = self.fb_cur, self.fb_aux
            self.screen_quad.render(self.program)
            flip = not flip
        self.program["flip"] = flip
        self.fb_cur.color_attachments[0].use(0)
        self.fb.color_attachments[0].use(1)
        self.program["blend"] = True
        target.use()
        self.screen_quad.render(self.program)
