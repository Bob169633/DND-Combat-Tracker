from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from Graphics_Options import get_graphics_images,get_image_display_name,resolve_image_path,saveable_image_path
try:
  from PIL import Image,ImageTk
  PIL_AVAILABLE=True
except ImportError:
  PIL_AVAILABLE=False
CHOOSE_IMAGE="Choose Image..."
USE_DEFAULT="Use Default PC Background"
class PlayerCardBackgroundsWindow:
  def __init__(self,root,players,on_save,background_color="black",mouse_x=None,mouse_y=None):
    self.root=root; self.players=players; self.on_save=on_save; self.background_color=background_color; self.rows=[]; self.preview_photo=None; self.image_display_to_path={}; self.custom_display_to_path={}; self.build_image_options(); self.window=tk.Toplevel(root); self.window.title("Player Card Backgrounds"); self.window.geometry("1320x840"); self.window.configure(bg=background_color); self.window.grab_set(); self.build_window(); self.place_window_at_mouse(mouse_x,mouse_y); self.grab_window_attention()
  def build_image_options(self):
    for ip in get_graphics_images():
      d=get_image_display_name(ip); base=d; n=2
      while d in self.image_display_to_path: d=f"{base} ({n})"; n+=1
      self.image_display_to_path[d]=saveable_image_path(ip)
  def get_display_for_path(self,p):
    if not p:return USE_DEFAULT
    for d,s in self.image_display_to_path.items():
      if s==p:return d
    for d,s in self.custom_display_to_path.items():
      if s==p:return d
    d=Path(p).stem.replace("_"," ").replace("-"," ").title() or "Custom Image"; self.custom_display_to_path[d]=p; return d
  def get_options(self): return [USE_DEFAULT]+list(self.image_display_to_path)+list(self.custom_display_to_path)+[CHOOSE_IMAGE]
  def get_path_for_display(self,d):
    if d==USE_DEFAULT:return ""
    return self.image_display_to_path.get(d,self.custom_display_to_path.get(d,""))
  def choose_image(self):
    f=filedialog.askopenfilename(title="Choose Player Card Background",filetypes=[("Image Files","*.jpg *.jpeg *.png *.webp"),("All Files","*.*")],parent=self.window)
    if not f:return None
    p=saveable_image_path(f); return self.get_display_for_path(p)
  def show_preview(self,d):
    if d==USE_DEFAULT:self.preview_photo=None; self.preview_label.config(image="",text="Uses the default PC card background from Config."); return
    fp=resolve_image_path(self.get_path_for_display(d))
    if not PIL_AVAILABLE or fp is None or not fp.exists(): self.preview_photo=None; self.preview_label.config(image="",text="Preview unavailable"); return
    try:
      im=Image.open(fp); im.thumbnail((720,720)); self.preview_photo=ImageTk.PhotoImage(im); self.preview_label.config(image=self.preview_photo,text="")
    except Exception:self.preview_photo=None; self.preview_label.config(image="",text="Preview unavailable")
  def selection_changed(self,row,sel):
    if sel==CHOOSE_IMAGE:
      chosen=self.choose_image()
      if chosen is None: row["var"].set(row["previous"]); return
      row["var"].set(chosen); row["previous"]=chosen; self.show_preview(chosen); return
    row["previous"]=sel; self.show_preview(sel)
  def place_window_at_mouse(self,x=None,y=None):
    if x is not None and y is not None:self.window.geometry(f"+{x+20}+{y+20}")
  def grab_window_attention(self): self.window.lift(); self.window.focus_force(); self.window.attributes("-topmost",True); self.window.after(250,lambda:self.window.attributes("-topmost",False))
  def build_window(self):
    c=tk.Frame(self.window,bg=self.background_color); c.pack(fill=tk.BOTH,expand=True,padx=20,pady=20); left=tk.Frame(c,bg=self.background_color); left.pack(side=tk.LEFT,fill=tk.Y,padx=(0,20)); right=tk.Frame(c,bg=self.background_color); right.pack(side=tk.LEFT,fill=tk.BOTH,expand=True); tk.Label(left,text="Player Character Backgrounds",font=("Arial",12,"bold"),bg=self.background_color,fg="white").pack(pady=(0,12))
    for p in self.players:
      rf=tk.Frame(left,bg=self.background_color); rf.pack(fill=tk.X,pady=5); tk.Label(rf,text=p.name,width=20,anchor="w",bg=self.background_color,fg="white").pack(side=tk.LEFT); cur=self.get_display_for_path(getattr(p,"card_background","")); v=tk.StringVar(value=cur); row={"player":p,"var":v,"previous":cur}; m=tk.OptionMenu(rf,v,*self.get_options(),command=lambda s,r=row:self.selection_changed(r,s)); m.config(width=28); m.pack(side=tk.LEFT,padx=5); self.rows.append(row)
    tk.Label(right,text="Preview",font=("Arial",12,"bold"),bg=self.background_color,fg="white").pack(pady=(0,12)); preview_box=tk.Frame(right,width=720,height=720,bg="gray10"); preview_box.pack(); preview_box.pack_propagate(False); self.preview_label=tk.Label(preview_box,text="Select a player background to preview it.",bg="gray10",fg="white"); self.preview_label.pack(fill=tk.BOTH,expand=True); b=tk.Frame(self.window,bg=self.background_color); b.pack(fill=tk.X,padx=20,pady=(0,18)); tk.Button(b,text="Save",width=12,command=self.save).pack(side=tk.RIGHT,padx=5); tk.Button(b,text="Cancel",width=12,command=self.window.destroy).pack(side=tk.RIGHT,padx=5)
  def save(self):
    self.on_save({getattr(r["player"],"combat_id",r["player"].name):self.get_path_for_display(r["var"].get()) for r in self.rows}); self.window.destroy()
