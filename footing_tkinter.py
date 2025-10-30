import tkinter as tk
from tkinter import ttk, messagebox
import math
from utils.is456_tables import get_tau_c, round_to_0_1, round_to_10

def suggest_reinforcement(Ast_req):
    """Suggest practical bar diameter and spacing."""
    bars = [12, 16, 20]
    for dia in bars:
        area_bar = math.pi * dia**2 / 4
        spacing = (1000 * area_bar) / Ast_req
        spacing = round_to_10(spacing)
        if spacing <= 250:
            return f"Provide {dia} mm φ bars @ {spacing} mm c/c both ways"
    return f"Provide 20 mm φ bars @ 200 mm c/c (minimum practical)"

def compute_design(P, cb, cd, SBC, fck, fy, cover, shape):
    Pu = 1.5 * P
    A = Pu / SBC
    if shape == "Square":
        B = L = round_to_0_1(math.sqrt(A))
    else:
        B = round_to_0_1(math.sqrt(A / 1.5))
        L = round_to_0_1(1.5 * B)
    q = Pu / (B * L)

    e = (B - cb/1000) / 2
    M = q * e**2 / 2
    d = round_to_10(max(math.sqrt((M*1e6)/(0.138*fck*1000)), 150))
    z = 0.9 * d
    Ast = (M*1e6)/(0.87*fy*z)
    pct = Ast/(1000*d)*100
    tau_c = get_tau_c(fck, pct)

    # Shear checks
    V = q * max(0, e - d/1000)
    v_one = (V*1000)/(1000*d)
    u = 2*(cb+cd)+8*d
    v_pun = (Pu*1000)/(u*d)

    return dict(Pu=Pu,A=A,B=B,L=L,q=q,M=M,d=d,Ast=Ast,pct=pct,
                v_one=v_one,v_pun=v_pun,tau_c=tau_c,
                one_ok=v_one<=tau_c,pun_ok=v_pun<=tau_c,
                reinf=suggest_reinforcement(Ast))

class FootingApp:
    def __init__(self,root):
        root.title("Isolated Footing Design (IS 456:2000 – Module V)")
        root.geometry("950x720")
        style=ttk.Style()
        style.configure(".",font=("Poppins",13))
        style.configure("TButton",font=("Poppins",13,"bold"))
        style.configure("Header.TLabel",font=("Poppins",18,"bold"))
        self.root=root; self.make_ui()

    def make_ui(self):
        f=ttk.Frame(self.root,padding=20); f.pack(fill="both",expand=True)
        ttk.Label(f,text="Isolated Footing Design Calculator",style="Header.TLabel").grid(row=0,column=0,columnspan=3,pady=8)
        self.vars={}
        fields=[("Column Load P (kN)",1000),
                ("Column Breadth (mm)",400),
                ("Column Depth (mm)",400),
                ("Safe Bearing Capacity (kN/m²)",200),
                ("fck (N/mm²)",25),
                ("fy (N/mm²)",415),
                ("Clear Cover (mm)",50)]
        for i,(lab,defv) in enumerate(fields,1):
            ttk.Label(f,text=lab).grid(row=i,column=0,sticky="e",pady=4)
            e=ttk.Entry(f); e.insert(0,str(defv))
            e.grid(row=i,column=1,sticky="ew",pady=4)
            self.vars[lab]=e
        ttk.Label(f,text="Footing Shape").grid(row=len(fields)+1,column=0,sticky="e")
        self.shape=tk.StringVar(value="Square")
        ttk.Combobox(f,textvariable=self.shape,values=["Square","Rectangular"],state="readonly").grid(row=len(fields)+1,column=1,sticky="ew")
        ttk.Button(f,text="Calculate Design",command=self.calculate).grid(row=len(fields)+2,column=0,columnspan=3,pady=10)
        self.txt=tk.Text(f,font=("Poppins",12),bg="white",height=15)
        self.txt.grid(row=len(fields)+3,column=0,columnspan=3,sticky="nsew")
        f.columnconfigure(1,weight=1); f.rowconfigure(len(fields)+3,weight=1)

    def calculate(self):
        try:
            P=float(self.vars["Column Load P (kN)"].get())
            cb=float(self.vars["Column Breadth (mm)"].get())
            cd=float(self.vars["Column Depth (mm)"].get())
            SBC=float(self.vars["Safe Bearing Capacity (kN/m²)"].get())
            fck=float(self.vars["fck (N/mm²)"].get())
            fy=float(self.vars["fy (N/mm²)"].get())
            cover=float(self.vars["Clear Cover (mm)"].get())
            R=compute_design(P,cb,cd,SBC,fck,fy,cover,self.shape.get())
            self.show(R)
        except Exception as e:
            messagebox.showerror("Error",str(e))

    def show(self,R):
        lines=[
            "IS 456:2000 – Isolated Footing Design (Module V)",
            "---------------------------------------------",
            f"Factored Load Pu = {R['Pu']:.1f} kN",
            f"Required Area = {R['A']:.3f} m²",
            f"Adopted Footing Size = {R['B']:.1f} m × {R['L']:.1f} m",
            f"Soil Pressure q = {R['q']:.1f} kN/m²",
            "",
            f"Effective Depth d = {R['d']:.0f} mm",
            f"Bending Moment = {R['M']:.2f} kNm/m width",
            f"Required Ast = {R['Ast']:.1f} mm²/m  (p = {R['pct']:.3f}%)",
            "",
            "Shear Checks:",
            f"  One-way v_u = {R['v_one']:.4f}  |  τ_c = {R['tau_c']:.4f}  →  {'OK' if R['one_ok'] else 'NOT OK'}",
            f"  Punching v_u = {R['v_pun']:.4f}  |  τ_c = {R['tau_c']:.4f}  →  {'OK' if R['pun_ok'] else 'NOT OK'}",
            "",
            f"Reinforcement Suggestion: {R['reinf']}",
            "",
            "All dimensions rounded to nearest 0.1 m (plan) and 10 mm (depth)."
        ]
        self.txt.delete("1.0","end")
        self.txt.insert("end","\n".join(lines))

if __name__=="__main__":
    root=tk.Tk(); FootingApp(root); root.mainloop()
