"""Module: interface.py
Overview: The core of the GUI for the A* demo.
Classes:
    Interface(object):
        Methods:
            __init__(self)
            make_background(self)
            reset(self,full=True)
            setup_barriers(self)
            render_text(self,specific=None)
            get_target(self)
            get_event(self,event)
            left_button_clicked(self)
            right_button_clicked(self)
            hotkeys(self,event)
            toggle_animate(self)
            toggle_piece(self,ind=None)
            add_barriers(self)
            update(self,Surf)
            found_solution(self)
            fill_cell(self,cell,color,Surf)
            center_number(self,cent,string,color,Surf)
            draw(self,Surf)
            draw_solve(self,Surf)
            draw_start_end_walls(self,Surf)
            draw_messages(self,Surf)"""
import pygame as pg
import solver

class Interface(object):
    def __init__(self):
        self.animate = False
        self.options = ("rook","queen","knight")
        self.piece_type = "rook"
        self.cell_size = (20,20)
        self.image = self.make_background()
        self.reset()
        self.font = pg.font.SysFont("arial",13)
        self.rendered = {}
        self.render_text()

    def make_background(self):
        """Create grid image. Currently screen and cell size are hardcoded."""
        image = pg.Surface((440,280)).convert()
        image.set_colorkey((255,0,255))
        image.fill((255,0,255),(20,20,400,240))
        for i in range(21):
            image.fill((255,0,0),(20+20*i,20,2,242))
        for i in range(13):
            image.fill((255,0,0),(20,20+20*i,400,2))
        return image

    def reset(self,full=True):
        """Allows both completely resetting the grid or resetting to an
        unsolved state."""
        if full:
            self.mode = "START"
            self.start_cell   = None
            self.goal_cell    = None
            self.barriers  = self.setup_barriers()
            self.Solver = None
            self.time_end = self.time_start = 0.0
            self.solution = []
        else:
            self.Solver = None
            self.mode = "BARRIER"

    def setup_barriers(self):
        """Initialize the boundary borders. Borders must be two cells thick to
        prevent knight pieces from leaving the grid."""
        self.add_barrier = False
        self.del_barrier = False
        barriers = set()
        for i in range(-1,23):
            for j in (-1,0,13,14):
                barriers.add((i,j))
        for j in range(-1,15):
            for i in (-1,0,21,22):
                barriers.add((i,j))
        return barriers

    def render_text(self,specific=None):
        """Prerender text messages. By default all are rendered. Single messages
        can be rerendered by passing a key corresponding to the below dictionary."""
        def render_each(specific,text_dict):
            msg,loc = text_dict[specific]
            rend = self.font.render(msg,1,(255,255,255))
            rect = pg.Rect(rend.get_rect(topleft=loc))
            self.rendered[specific] = [rend,rect]
        text = {"START"   : ["Place your start point:",(10,1)],
                "GOAL"    : ["Place your goal:",(10,1)],
                "BARRIER" : ["Draw your walls or press spacebar to solve:",(10,1)],
                "ENTER"   : ["Press 'Enter' to restart.",(10,1)],
                "RESET"   : ["Press 'i' to reset.",(150,1)],
                "ANIM"    : ["Animation: {}".format(["Off","On"][self.animate]),(340,1)],
                "MOVE"    : ["Move type: {}".format(self.piece_type.capitalize()),(320,263)],
                "TIME"    : ["Time (ms): {}".format(self.time_end-self.time_start),(100,263)],
                "FAILED"  : ["No solution.",(20,263)],
                "SOLVED"  : ["Steps: {}".format(len(self.solution)),(20,263)]}
        if specific:
            render_each(specific,text)
        else:
            for specific in text:
                render_each(specific,text)

    def get_target(self):
        """Find both the exact mouse position and its position in graph cells."""
        self.mouse  = pg.mouse.get_pos()
        self.target = (self.mouse[0]//self.cell_size[0],self.mouse[1]//self.cell_size[1])

    def get_event(self,event):
        """Receives events from the control class and passes them along as appropriate."""
        self.get_target()
        if event.type == pg.MOUSEBUTTONDOWN:
            hit = pg.mouse.get_pressed()
            if hit[0]:
                self.left_button_clicked()
            elif hit[2]:
                self.right_button_clicked()
        elif event.type == pg.MOUSEBUTTONUP:
            self.add_barrier = False
            self.del_barrier = False
        elif event.type == pg.KEYDOWN:
            self.hotkeys(event)

    def left_button_clicked(self):
        """Left mouse button functionality for get_event method."""
        if pg.Rect(20,20,400,240).collidepoint(self.mouse):
            if self.mode == "START":
                if self.target != self.goal_cell and self.target not in self.barriers:
                    self.start_cell = self.target
                    self.mode = ("BARRIER" if self.goal_cell else "GOAL")
            elif self.mode == "GOAL":
                if self.target != self.start_cell and self.target not in self.barriers:
                    self.goal_cell = self.target
                    self.mode = "BARRIER"
            elif self.mode == "BARRIER":
                self.add_barrier = True
        elif self.rendered["MOVE"][1].collidepoint(self.mouse):
            self.toggle_piece()
        elif self.rendered["ANIM"][1].collidepoint(self.mouse):
            self.toggle_animate()
        elif self.mode == "BARRIER" and self.rendered["BARRIER"][1].collidepoint(self.mouse):
            self.mode = "RUN"
        elif self.mode in ("SOLVED","FAILED"):
            if self.rendered["ENTER"][1].collidepoint(self.mouse):
                self.reset()
            elif self.rendered["RESET"][1].collidepoint(self.mouse):
                self.reset(False)

    def right_button_clicked(self):
        """Right mouse button functionality for get_event method."""
        if self.mode != "RUN":
            if self.target == self.start_cell:
                self.start_cell = None
                self.mode = "START"
            elif self.target == self.goal_cell:
                self.goal_cell = None
                self.mode = ("GOAL" if self.start_cell else "START")
            elif self.mode == "BARRIER":
                self.del_barrier = True

    def hotkeys(self,event):
        """Keyboard functionality for get_event method."""
        if event.key in (pg.K_1,pg.K_2,pg.K_3):
            self.toggle_piece(int(event.unicode)-1)
        elif event.key == pg.K_d:
            self.toggle_animate()
        elif self.mode == "BARRIER" and event.key == pg.K_SPACE:
            self.mode = "RUN"
        elif self.mode in ("SOLVED","FAILED"):
             if event.key == pg.K_RETURN:
                self.reset()
             elif event.key == pg.K_i:
                self.reset(False)

    def toggle_animate(self):
        """Turns animation mode on and off."""
        if self.mode != "RUN":
            self.animate = not self.animate
            self.render_text("ANIM")
    def toggle_piece(self,ind=None):
        """Change to next piece or to a specific piece if ind is supplied."""
        if self.mode != "RUN":
            if not ind:
                ind = (self.options.index(self.piece_type)+1)%len(self.options)
            self.piece_type = self.options[ind]
            self.render_text("MOVE")

    def add_barriers(self):
        """Controls both adding and deleting barrier cells with the mouse."""
        if self.mode == "BARRIER":
            self.get_target()
            if pg.Rect(20,20,400,240).collidepoint(self.mouse):
                if self.target not in (self.start_cell,self.goal_cell):
                    if self.add_barrier:
                        self.barriers.add(self.target)
                    elif self.del_barrier:
                        self.barriers.discard(self.target)

    def update(self,Surf):
        """Primary update logic control flow for the GUI."""
        self.add_barriers()
        if self.mode == "RUN":
            if not self.Solver:
                self.time_start = pg.time.get_ticks()
                self.Solver = solver.Star(self.start_cell,self.goal_cell,self.piece_type,self.barriers)
            if self.animate:
                self.Solver.evaluate()
            else:
                while not self.Solver.solution:
                    self.Solver.evaluate()
            if self.Solver.solution:
                self.found_solution()
        if self.mode != "RUN" or self.animate:
            self.draw(Surf)

    def found_solution(self):
        """Sets appropriate mode when solution is found (or failed)."""
        self.time_end = pg.time.get_ticks()
        if self.Solver.solution == "NO SOLUTION":
            self.mode = "FAILED"
        else:
            self.solution = self.Solver.solution
            self.mode = "SOLVED"
            self.render_text("SOLVED")
        self.render_text("TIME")

    def fill_cell(self,cell,color,Surf):
        """Fills a single cell given coordinates, color, and a target Surface."""
        loc = cell[0]*self.cell_size[0],cell[1]*self.cell_size[1]
        Surf.fill(color,(loc,self.cell_size))
        return pg.Rect(loc,self.cell_size)
    def center_number(self,cent,string,color,Surf):
        """Used for centering numbers on cells."""
        rend = self.font.render(string,1,color)
        rect = pg.Rect(rend.get_rect(center=cent))
        rect.move_ip(1,1)
        Surf.blit(rend,rect)

    def draw(self,Surf):
        """Calls draw functions in the appropraite order."""
        Surf.fill(0)
        self.draw_solve(Surf)
        self.draw_start_end_walls(Surf)
        Surf.blit(self.image,(0,0))
        self.draw_messages(Surf)
    def draw_solve(self,Surf):
        """Draws while solving (if animate is on) and once solved."""
        if self.mode in ("RUN","SOLVED","FAILED"):
            for cell in self.Solver.closed_set:
                self.fill_cell(cell,(255,0,255),Surf)
            if self.mode == "SOLVED":
                for i,cell in enumerate(self.solution):
                    cent = self.fill_cell(cell,(0,255,0),Surf).center
                    self.center_number(cent,str(len(self.solution)-i),(0,0,0),Surf)
    def draw_start_end_walls(self,Surf):
        """Draw endpoints and barriers."""
        if self.start_cell:
            self.fill_cell(self.start_cell,(255,255,0),Surf)
        if self.goal_cell:
            cent = self.fill_cell(self.goal_cell,(0,0,255),Surf).center
            if self.mode == "SOLVED":
                self.center_number(cent,str(len(self.solution)),(255,255,255),Surf)
        for cell in self.barriers:
            self.fill_cell(cell,(255,255,255),Surf)
    def draw_messages(self,Surf):
        """Draws the text (not including cell numbers)."""
        for key in [self.mode,"MOVE","ANIM"]:
            try:
                Surf.blit(*self.rendered[key])
            except KeyError:
                pass
        if self.mode in ("SOLVED","FAILED"):
            for rend in ("TIME","RESET","ENTER"):
                Surf.blit(*self.rendered[rend])