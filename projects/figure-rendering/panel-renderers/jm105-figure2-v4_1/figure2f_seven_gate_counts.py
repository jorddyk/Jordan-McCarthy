#!/usr/bin/env python3
"""Render JM105 Figure 2F from the raw 402-row gate table.

Figure 2 scope: total/rRNA-depleted JM105 only.
NMD_hidden = IR(upf1Δ) - IR(UPF1+).
No automatic tight crop; fixed 92 x 82 mm canvas; editable SVG text.
"""
from __future__ import annotations
import argparse, csv, json, os
from datetime import datetime, timezone
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib.text import Text
import pandas as pd

RAW = Path("/cluster/scratch/jmccarthy/JM105_RNAseq/Figure2_stage1_audit_20260630_145204/Figure2_stage1B_STRICT_NUCLEAR_ORF_GATE/Figure_2_STRICT_candidate_metrics_all.tsv")
ROOT = Path("/cluster/scratch/jmccarthy/JM105_RNAseq")
MM = 25.4
SIZE = (92.0, 82.0)
GATES = [
 (1,"High-confidence spliceosomal intron\n(annotated)",["pass_annotation_gate"]),
 (2,"Intron in protein-coding host gene",["pass_strict_nuclear_orf_gate"]),
 (3,"Adequate support (>10 reads in NMD-off,\none condition)",["pass_count_gate"]),
 (4,"Matched NMD on/off values in all\nthree conditions",["pass_required_conditions_gate"]),
 (5,"No floor artifacts in NMD-off\n(IR > 0.01)",["pass_floor_gate","pass_old2_nmd_sensitive_gate"]),
 (6,"Age effect threshold\n(old 2% − young 2% > 0.15)",["pass_age_gate"]),
 (7,"CR suppression threshold\n(old 2% − old 0.1% CR > 0.15)",["pass_cr_gate"]),
]
REQ = [column for _,_,columns in GATES for column in columns] + ["candidate_passed_strict"]

def boolean(series):
    if pd.api.types.is_bool_dtype(series): return series.fillna(False)
    return series.astype("string").str.strip().str.lower().isin({"true","1","yes","y","t","pass","passed"})

def write_tsv(path, rows):
    rows=list(rows); fields=[]
    for row in rows:
        for key in row:
            if key not in fields: fields.append(key)
    with Path(path).open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields,delimiter="\t"); writer.writeheader(); writer.writerows(rows)

def derive(path):
    frame=pd.read_csv(path,sep="\t",low_memory=False)
    missing=[column for column in REQ if column not in frame.columns]
    if missing: raise RuntimeError(f"Missing gate columns: {missing}")
    if len(frame)!=402: raise RuntimeError(f"Expected 402 rows; found {len(frame)}")
    for column in REQ: frame[column]=boolean(frame[column])
    mask=pd.Series(True,index=frame.index); previous=len(frame); rows=[]; cumulative=[]
    for number,label,columns in GATES:
        cumulative.extend(columns)
        for column in columns: mask &= frame[column]
        count=int(mask.sum())
        rows.append({"gate":number,"visible_label":label.replace("\n"," "),"new_columns":" & ".join(columns),"cumulative_predicate":" & ".join(cumulative),"n":count,"loss":previous-count})
        previous=count
    mismatch=mask != frame["candidate_passed_strict"]
    if mismatch.any(): raise RuntimeError(f"Final mask differs from candidate_passed_strict for {int(mismatch.sum())} rows")
    if int(mask.sum())!=49: raise RuntimeError(f"Expected final n=49; found {int(mask.sum())}")
    return rows

def configure(family):
    matplotlib.rcParams.update({"font.family":"sans-serif","font.sans-serif":[family],"svg.fonttype":"none","pdf.fonttype":42,"ps.fonttype":42,"savefig.dpi":300})

def draw(rows,family):
    configure(family); fig=plt.figure(figsize=(SIZE[0]/MM,SIZE[1]/MM),facecolor="none"); fig.patch.set_alpha(0)
    ax=fig.add_axes([0,0,1,1]); ax.set(xlim=(0,1),ylim=(0,1)); ax.axis("off")
    top=.965; height=.086; gap=.014
    for index,((number,label,_),row) in enumerate(zip(GATES,rows)):
        y=top-(index+1)*height-index*gap
        ax.add_patch(FancyBboxPatch((.035,y),.93,height,boxstyle="round,pad=.006,rounding_size=.012",facecolor="white",edgecolor="#C9CDD2",linewidth=1,transform=ax.transAxes))
        ax.add_patch(Circle((.087,y+height/2),.020,facecolor="#0B67C2",edgecolor="none",transform=ax.transAxes))
        ax.text(.087,y+height/2,str(number),ha="center",va="center",fontsize=6.3,color="white",fontweight="bold",transform=ax.transAxes)
        ax.text(.128,y+height/2,label,ha="left",va="center",fontsize=6.25,color="#202124",linespacing=.96,transform=ax.transAxes)
        ax.text(.885,y+height/2,f"n={row['n']}",ha="right",va="center",fontsize=6.6,color="#202124",fontweight="bold",transform=ax.transAxes)
        cy=y+height/2
        ax.plot([.930,.939],[cy-.002,cy-.012],color="#70B62C",lw=1.5,solid_capstyle="round",transform=ax.transAxes,clip_on=False)
        ax.plot([.939,.954],[cy-.012,cy+.013],color="#70B62C",lw=1.5,solid_capstyle="round",transform=ax.transAxes,clip_on=False)
    ax.add_patch(FancyBboxPatch((.06,.035),.88,.165,boxstyle="round,pad=.010,rounding_size=.014",facecolor="#E7F1EB",edgecolor="#E66700",linewidth=1.2,transform=ax.transAxes))
    ax.text(.5,.135,"High-confidence, age-increased, CR-suppressed",ha="center",va="center",fontsize=7,color="#E66700",fontweight="bold",transform=ax.transAxes)
    ax.text(.5,.080,f"candidate set  (n={rows[-1]['n']} introns)",ha="center",va="center",fontsize=7,color="#202124",fontweight="bold",transform=ax.transAxes)
    return fig

def audit(fig):
    fig.canvas.draw(); renderer=fig.canvas.get_renderer(); outer=fig.bbox; items=[]
    for artist in fig.findobj(match=Text):
        if artist.get_visible() and artist.get_text().strip(): items.append((artist.get_text().strip(),artist.get_window_extent(renderer)))
    clipped=[text for text,box in items if box.x0<outer.x0-.5 or box.y0<outer.y0-.5 or box.x1>outer.x1+.5 or box.y1>outer.y1+.5]
    overlaps=[]
    for index,(a,ab) in enumerate(items):
        for b,bb in items[index+1:]:
            xo=min(ab.x1,bb.x1)-max(ab.x0,bb.x0); yo=min(ab.y1,bb.y1)-max(ab.y0,bb.y0)
            if xo>1 and yo>1: overlaps.append({"a":a,"b":b,"x_px":round(float(xo),2),"y_px":round(float(yo),2)})
    return {"clipped":clipped,"overlaps":overlaps,"text_count":len(items)}

def save(fig,out):
    stem=out/"Figure_2F_seven_gate_selection"; paths={"svg":Path(str(stem)+".transparent.svg"),"pdf":Path(str(stem)+".transparent.pdf"),"png":Path(str(stem)+".transparent.png"),"preview":Path(str(stem)+".preview_white.png")}
    fig.patch.set_alpha(0)
    for key in ("svg","pdf","png"): fig.savefig(paths[key],transparent=True,facecolor="none")
    fig.patch.set_facecolor("white"); fig.patch.set_alpha(1); fig.savefig(paths["preview"],transparent=False,facecolor="white")
    return {key:str(value) for key,value in paths.items()}

def inventory(root,path):
    rows=[]
    for directory,subdirs,files in os.walk(root):
        subdirs.sort(); files.sort()
        for name in files:
            item=Path(directory)/name
            try: stat=item.stat()
            except OSError: continue
            rows.append({"path":str(item),"size_bytes":stat.st_size,"modified_utc":datetime.fromtimestamp(stat.st_mtime,tz=timezone.utc).isoformat()})
    write_tsv(path,rows); return len(rows)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--raw-table",type=Path,default=RAW); parser.add_argument("--project-root",type=Path,default=ROOT); parser.add_argument("--out",type=Path,required=True); parser.add_argument("--skip-inventory",action="store_true"); args=parser.parse_args()
    out=args.out.resolve(); out.mkdir(parents=True,exist_ok=True); rows=derive(args.raw_table); write_tsv(out/"Figure_2F_seven_gate_counts.tsv",rows)
    font_audits=[]
    for family in ("Liberation Sans","DejaVu Sans"):
        fig=draw(rows,family); result=audit(fig); resolved=font_manager.FontProperties(fname=font_manager.findfont(font_manager.FontProperties(family=[family]))).get_name(); result.update({"requested":family,"resolved":resolved}); font_audits.append(result); plt.close(fig)
        if result["clipped"] or result["overlaps"]: raise RuntimeError(f"Collision under {family}: {result}")
    fig=draw(rows,"DejaVu Sans"); final=audit(fig)
    if final["clipped"] or final["overlaps"]: raise RuntimeError(f"Final collision: {final}")
    paths=save(fig,out); plt.close(fig); file_count=0 if args.skip_inventory else inventory(args.project_root,out/"JM105_Euler_file_inventory.tsv")
    payload={"raw_table":str(args.raw_table),"counts":[row["n"] for row in rows],"final_equals_candidate_passed_strict":True,"font_audits":font_audits,"final_audit":final,"inventory_file_count":file_count,"outputs":paths}
    (out/"Figure_2F_seven_gate_audit.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print("FIGURE2F_SEVEN_GATE_RENDER_COMPLETE"); print("COUNTS="+" -> ".join(map(str,payload["counts"]))); print(f"OUT={out}"); print(f"PREVIEW={paths['preview']}"); print(f"INVENTORY_FILE_COUNT={file_count}")
if __name__=="__main__": main()
