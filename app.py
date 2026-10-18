from flask import Flask, Response, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timezone
import json
import math
import os
import re
import secrets

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from pymongo.errors import PyMongoError, DuplicateKeyError
except ImportError:
    MongoClient = None
    ASCENDING = 1
    DESCENDING = -1
    class PyMongoError(Exception):
        pass
    class DuplicateKeyError(PyMongoError):
        pass

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)
app.config['MAX_CONTENT_LENGTH'] = 96 * 1024
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'true').strip().lower() in ('1', 'true', 'yes', 'on')

HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<meta name="theme-color" content="#050907">
<title>Florida Shadows: The Definitive Nightmare</title>
<style>
:root {
  color-scheme: dark;
  --ink: #e9e6d6;
  --muted: #9ba99a;
  --red: #b83d40;
  --red-hot: #ef5c54;
  --gold: #d4bc80;
  --green: #92a789;
  --panel: rgba(5, 10, 8, .95);
  --line: #536253;
  --gap: 12px;
}
* {
  box-sizing: border-box;
  -webkit-tap-highlight-color: transparent;
}
html,
body {
  width: 100%;
  height: 100%;
  margin: 0;
  overflow: hidden;
  background: #030605;
  color: var(--ink);
  font-family: Consolas, Monaco, "Courier New", monospace;
}
body {
  user-select: none;
}
button,
input {
  font: inherit;
}
button {
  color: var(--ink);
  border: 1px solid #667563;
  background: linear-gradient(180deg, #253027, #111713);
  padding: 12px 15px;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  transition: border-color .12s ease, background .12s ease, transform .12s ease;
}
button:hover,
button:focus-visible {
  border-color: var(--gold);
  background: linear-gradient(180deg, #49302a, #211715);
  outline: 1px solid #b89d60;
}
button:active {
  transform: translateY(1px);
}
button.selected {
  border-color: var(--gold);
  background: linear-gradient(180deg, #3d3b28, #20251a);
  box-shadow: inset 0 0 0 1px #928052, 0 0 14px #d6b56a18;
}
button:disabled {
  opacity: .35;
  cursor: not-allowed;
}
#game {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
  image-rendering: pixelated;
  background: #09110d;
  cursor: crosshair;
}
body.prologue-mode #hud { display: none !important; }
body.prologue-mode.prologue-call #touchControls,
body.prologue-mode.prologue-arrival #touchControls { display: none !important; }
body.prologue-mode.prologue-drive.mobile-mode #touchControls { display: block; }
#hud {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  text-shadow: 0 2px 4px #000;
}
#topbar {
  position: absolute;
  top: 13px;
  left: 13px;
  right: 13px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}
.hudbox {
  max-width: min(350px, 54vw);
  padding: 10px 12px;
  background: rgba(4, 8, 6, .82);
  border: 1px solid #536253;
  box-shadow: 0 4px 18px #0008;
  font-size: 11px;
  line-height: 1.55;
}
.hudbox b {
  font-size: 10px;
  color: #e0d4b4;
  letter-spacing: 1.6px;
}
.micro {
  color: #879589;
  font-size: 9px;
  letter-spacing: .8px;
  line-height: 1.55;
}
#objective {
  max-width: 330px;
  color: #e5d19a;
  margin-top: 6px;
}
#status {
  color: #e18a81;
  margin-top: 4px;
}
#survivorLocator {
  display:none;
  position:fixed;
  z-index:8;
  top:116px;
  left:50%;
  transform:translateX(-50%);
  width:min(330px,86vw);
  padding:8px 12px 9px;
  border:1px solid #8aa978;
  border-left:4px solid #b9e18b;
  background:linear-gradient(110deg,rgba(7,18,11,.96),rgba(15,34,19,.93));
  box-shadow:0 0 18px rgba(130,205,105,.17),0 5px 20px #0009;
  color:#e3efcf;
  text-align:left;
  pointer-events:none;
  text-shadow:0 2px 4px #000;
  animation:locatorPulse 2.3s ease-in-out infinite;
}
#survivorLocator.visible { display:block; }
#survivorLocator .locator-kicker { color:#b0d28e; font-size:9px; letter-spacing:1.8px; margin-bottom:4px; }
#survivorLocator .locator-main { font-weight:bold; font-size:12px; letter-spacing:.5px; }
#survivorLocator .locator-sub { margin-top:4px; color:#b3c2aa; font-size:10px; line-height:1.45; }
#survivorLocator .locator-range { color:#f0dd9a; }
@keyframes locatorPulse { 0%,100% { box-shadow:0 0 12px rgba(130,205,105,.12),0 5px 20px #0009; } 50% { box-shadow:0 0 23px rgba(130,205,105,.28),0 5px 20px #0009; } }
#healthbar,
#staminabar {
  width: 152px;
  height: 7px;
  background: #171d17;
  border: 1px solid #79816e;
  margin-top: 5px;
}
#healthfill {
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, #79282a, #d04a42);
}
#staminafill {
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, #667c4a, #b7c77e);
}
#bottom {
  position: absolute;
  left: 13px;
  right: 13px;
  bottom: 13px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
}
#prompt {
  color: #e6d49f;
  min-height: 17px;
  margin-bottom: 5px;
}
#minimap {
  width: 132px;
  height: 132px;
  flex: 0 0 auto;
  border: 1px solid #82907c;
  background: #07100bde;
  box-shadow: 0 0 18px #0009;
}
#objectiveToggle {
  pointer-events: auto;
  position: absolute;
  top: 50%;
  right: 0;
  writing-mode: vertical-rl;
  border-right: 0;
  padding: 13px 8px;
  font-size: 10px;
  background: #09100cdb;
}
#toast {
  display: none;
  position: fixed;
  z-index: 12;
  left: 50%;
  top: 21%;
  transform: translateX(-50%);
  width: max-content;
  max-width: 90vw;
  padding: 12px 17px;
  background: #080c09f5;
  border: 1px solid var(--gold);
  box-shadow: 0 0 32px #000;
  color: #f0dda8;
  font-size: 12px;
  line-height: 1.5;
  letter-spacing: .5px;
  text-align: center;
}
.overlay {
  position: fixed;
  z-index: 5;
  inset: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: auto;
  padding: clamp(10px, 3vw, 30px);
  background: radial-gradient(ellipse at 48% 42%, rgba(15, 33, 24, .58), rgba(0, 0, 0, .87) 61%, rgba(0, 0, 0, .98));
}
.panel {
  position: relative;
  width: min(900px, 97vw);
  max-height: 94vh;
  overflow: auto;
  padding: clamp(20px, 4vw, 42px);
  background: linear-gradient(135deg, rgba(13, 22, 16, .98), rgba(4, 8, 6, .99));
  border: 1px solid #697966;
  box-shadow: 0 0 0 5px #000b, 0 0 76px #000;
  scrollbar-color: #54624f #101610;
}
.panel::before {
  content: "";
  position: absolute;
  inset: 7px;
  border: 1px solid #3a493b;
  pointer-events: none;
  opacity: .7;
}
.panel > * {
  position: relative;
}
.hidden {
  display: none !important;
}
#disclaimerPanel {
  z-index: 50;
  background: radial-gradient(ellipse at center, rgba(23, 31, 23, .96), rgba(0, 0, 0, .98) 75%);
}
#disclaimerPanel .panel { border-color: #a89565; }
.disclaimer-callout {
  border: 1px solid #765f3d;
  background: rgba(42, 31, 19, .46);
  padding: 13px 15px;
  color: #e6d9b8;
  line-height: 1.65;
  font-size: 12px;
}
.disclaimer-choice { display:flex; align-items:flex-start; gap:10px; color:#c7d0c2; font-size:12px; line-height:1.6; margin:15px 0; }
.disclaimer-choice input { accent-color:#b9a06a; margin-top:3px; width:17px; height:17px; }
#personalScare {
  display:none;
  position:fixed;
  inset:0;
  z-index:99999;
  align-items:center;
  justify-content:center;
  overflow:hidden;
  pointer-events:none;
  background:#010202;
  image-rendering:pixelated;
  isolation:isolate;
}
#personalScare.active { display:flex; animation:scareScreenHit 2.05s steps(2,end) both; }
#personalScare::before {
  content:"";
  position:absolute;
  z-index:4;
  inset:-15%;
  opacity:.8;
  background:repeating-linear-gradient(0deg,transparent 0 2px,rgba(202,225,209,.19) 3px,transparent 4px 7px),repeating-linear-gradient(90deg,rgba(223,20,30,.14) 0 2px,transparent 2px 8px);
  mix-blend-mode:screen;
  animation:infoStatic .075s steps(2,end) infinite;
}
#personalScare::after {
  content:"SIGNAL OVERRIDE // YOU ARE NOT ALONE";
  position:absolute;
  z-index:1;
  left:0;right:0;top:4%;
  color:#d33b3c;
  text-align:center;
  font:bold clamp(11px,2vw,18px)/1.2 Consolas,monospace;
  letter-spacing:clamp(2px,.7vw,8px);
  text-shadow:3px 0 #e7ddd0,-3px 0 #720b13,0 0 15px #db101c;
  opacity:.82;
  background:linear-gradient(transparent 32%,rgba(105,0,7,.19) 33% 65%,transparent 66%);
  padding:8px;
  animation:stampFlicker .13s steps(2,end) infinite;
}
.scare-face {
  position:absolute;
  width:min(67vw,680px);
  height:min(86vh,760px);
  min-width:220px;
  min-height:320px;
  top:2%;
  left:50%;
  transform:translateX(-50%);
  clip-path:polygon(23% 0,77% 0,90% 12%,97% 35%,92% 62%,80% 85%,67% 100%,33% 100%,20% 85%,8% 62%,3% 35%,10% 12%);
  z-index:2;
  background:radial-gradient(ellipse at 50% 26%,rgba(137,150,126,.42) 0%,rgba(82,96,74,.24) 28%,transparent 57%),linear-gradient(90deg,#030403 0%,#182019 9%,#3b4838 18%,#677260 27%,#303b2c 37%,#10150f 48%,#303a2b 58%,#5a674f 70%,#273023 81%,#080a07 95%,#010201 100%);
  box-shadow:0 0 70px #810e18, inset 0 0 50px #000;
  filter:drop-shadow(0 0 22px #e20c21) contrast(1.45);
  animation:faceJolt .09s steps(2,end) infinite;
}
.scare-face::before {
  content:"";
  position:absolute;
  inset:0;
  background:repeating-linear-gradient(0deg,transparent 0 16px,rgba(0,0,0,.78) 17px 22px,transparent 23px 37px),linear-gradient(110deg,transparent 0 20%,rgba(116,130,107,.22) 31%,transparent 43% 61%,rgba(112,121,103,.14) 75%,transparent 82%);
  opacity:.58;
}
.scare-face .scare-eye { position:absolute; top:32%; width:24%; height:8%; background:#fff0df; box-shadow:0 0 17px 9px #f21d2e,0 0 75px 28px #a90e19; }
.scare-face .scare-eye.left { left:14%; transform:rotate(11deg) skewX(-18deg); }
.scare-face .scare-eye.right { right:14%; transform:rotate(-11deg) skewX(18deg); }
.scare-face .scare-nose { position:absolute; left:40%; top:37%; width:20%; height:23%; background:linear-gradient(90deg,#050705,#080a07 45%,#262c22 70%,#020302); border-left:4px solid #151a13; clip-path:polygon(50% 0,100% 100%,0 100%); filter:drop-shadow(0 0 4px #68705d); }
.scare-face .scare-mouth { position:absolute; left:14%; right:14%; top:61%; height:22%; background:#020202; border:4px solid #651b21; clip-path:polygon(0 0,100% 0,94% 100%,80% 65%,70% 100%,58% 61%,48% 100%,36% 63%,25% 100%,12% 62%); box-shadow:0 0 30px #e20b24; overflow:hidden; }
.scare-face .scare-mouth::before { content:""; position:absolute; left:2%; right:2%; top:0; height:42%; background:repeating-linear-gradient(90deg,#ded8c6 0 12px,#191715 12px 18px); clip-path:polygon(0 0,100% 0,92% 100%,80% 12%,70% 100%,58% 12%,48% 100%,38% 12%,28% 100%,17% 12%,8% 100%); }
.scare-face .scare-mouth::after { content:""; position:absolute; left:24%; right:20%; bottom:0; height:27%; background:#610b17; box-shadow:0 0 16px #c10d25; clip-path:polygon(0 0,100% 0,73% 100%,25% 76%); }
.scare-entity {
  display:none;
  position:absolute;
  left:50%;top:9%;height:78%;width:min(55vw,540px);
  z-index:2;
  transform:translateX(-50%);
  filter:drop-shadow(0 0 22px #cf101d);
  animation:entityLunge .17s steps(2,end) infinite;
}
.scare-entity .entity-head { position:absolute;top:0;left:35%;width:30%;height:23%;background:#020303;clip-path:polygon(18% 0,82% 0,100% 40%,77% 100%,24% 100%,0 40%);box-shadow:0 0 20px #100; }
.scare-entity .entity-eyes { position:absolute;top:12%;left:39%;width:22%;height:3%;background:#f5ead1;box-shadow:0 0 17px 9px #b90a17; }
.scare-entity .entity-body { position:absolute;top:20%;left:24%;width:52%;height:62%;background:linear-gradient(90deg,#000 0 20%,#101310 43%,#030403 64%,#111411);clip-path:polygon(27% 0,73% 0,86% 17%,100% 100%,64% 91%,51% 49%,36% 93%,0 100%,14% 18%); }
.scare-entity .entity-arm { position:absolute;top:27%;width:15%;height:58%;background:#030403;transform-origin:top; }
.scare-entity .entity-arm.left { left:23%;transform:rotate(12deg); }
.scare-entity .entity-arm.right { right:23%;transform:rotate(-12deg); }
#personalScare.variant-contact .scare-face { display:none; }
#personalScare.variant-contact .scare-entity { display:block; }
#personalScare.variant-duplicate .scare-face { width:min(84vw,850px); filter:drop-shadow(-17px 0 #bb0714) drop-shadow(17px 0 #e5ded2) contrast(1.7); }
#personalScare.variant-duplicate .scare-face .scare-eye { height:11%;top:30%;background:#fff7df;box-shadow:0 0 22px 12px #e71025,0 0 90px 33px #a90e19; }
#personalScare.variant-duplicate .scare-face::before { background:repeating-linear-gradient(0deg,transparent 0 8px,#e6e3d5 9px 11px,transparent 12px 27px); opacity:.35; }
#personalScare.variant-address .scare-face { width:min(48vw,510px); height:61vh; top:0; filter:drop-shadow(0 0 24px #d50019) contrast(1.8); transform:translateX(-50%) scaleX(.74); }
#personalScare.variant-address .scare-copy { bottom:17%; transform:skewY(-1deg); border-color:#e52d39; box-shadow:0 0 60px #b80016; }
#personalScare.variant-personnel .scare-face { width:min(88vw,940px); height:min(110vh,980px); top:-11%; }
.scare-copy {
  position:absolute;
  z-index:6;
  bottom:5%;
  width:min(800px,94vw);
  border:2px solid #a33d40;
  background:rgba(2,3,3,.97);
  padding:clamp(14px,3vw,28px);
  text-align:center;
  box-shadow:0 0 44px #6f101c, inset 0 0 26px #230406;
  transform:perspective(600px) rotateX(2deg);
}
.scare-copy h2 { color:#fff0e5; font-size:clamp(18px,4vw,36px); margin:0 0 10px; letter-spacing:clamp(2px,.5vw,7px); text-shadow:3px 0 #be1020,-2px 0 #34504a,0 0 18px #a00010; animation:textGlitch .15s steps(2,end) infinite; }
.scare-copy pre { white-space:pre-line; font:bold clamp(12px,2vw,18px)/1.5 Consolas,monospace; color:#fff2dc; margin:0; text-shadow:2px 0 #800; }
.scare-copy small { display:block; margin-top:9px; color:#ff6666; font-size:10px; letter-spacing:2px; }
@keyframes scareScreenHit { 0% { opacity:0; transform:scale(1.18) translateX(0); filter:contrast(2); background:#fff; } 4% { opacity:1; transform:scale(1.01) translateX(-14px); background:#f5eee2; } 9% { opacity:1; transform:scale(1.04) translateX(12px); background:#240004; } 16% { opacity:.12; transform:scale(.98) translateX(-8px); } 23% { opacity:1; transform:scale(1.03) translateX(7px); background:#030303; } 39% { opacity:1; transform:scale(1.01) translateX(-3px); } 100% { opacity:1; transform:none; filter:none; } }
@keyframes infoStatic { 0% { transform:translate(0,0) skewX(0); } 33% { transform:translate(-3%,1%) skewX(3deg); } 66% { transform:translate(2%,-2%) skewX(-2deg); } 100% { transform:translate(-1%,2%); } }
@keyframes faceJolt { 0% { margin-left:-8px; transform:translateX(-50%) scale(1.08); } 50% { margin-left:9px; transform:translateX(-50%) scale(1.015); } 100% { margin-left:-3px; transform:translateX(-50%) scale(1.10); } }
@keyframes entityLunge { 0% { margin-top:3vh; transform:translateX(-50%) scale(1.2); } 50% { margin-top:-1vh; transform:translateX(-50%) scale(1.06); } 100% { margin-top:2vh; transform:translateX(-50%) scale(1.24); } }
@keyframes stampFlicker { 0%,100% { opacity:.8; transform:translateX(0); } 50% { opacity:.22; transform:translateX(4px); } }
@keyframes textGlitch { 0%,100% { transform:translateX(0); } 50% { transform:translateX(2px); text-shadow:-3px 0 #b10b1a,3px 0 #ddd; } }
@media (prefers-reduced-motion: reduce) { #personalScare::before,.scare-face,.scare-entity,.scare-copy h2 { animation:none; } }
.kicker {
  color: #b6c2b0;
  font-size: 10px;
  letter-spacing: 4px;
  text-transform: uppercase;
}
.logo {
  margin: 19px 0 15px;
  color: #e9e5d7;
  font-size: clamp(42px, 8vw, 84px);
  font-weight: 900;
  line-height: .82;
  letter-spacing: clamp(1px, .4vw, 5px);
  text-shadow: 4px 4px #41181b, 7px 7px #020403;
}
.logo span {
  color: #c34749;
}
.subtitle {
  color: #c8b886;
  font-size: clamp(10px, 1.7vw, 14px);
  letter-spacing: clamp(1px, .35vw, 4px);
}
.intro {
  max-width: 630px;
  color: #b9c3b6;
  font-size: 13px;
  line-height: 1.8;
}
.menu-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(220px, .85fr);
  align-items: center;
  gap: 26px;
}
.menu-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 9px;
  margin-top: 23px;
}
.menu-actions button:first-child {
  grid-column: 1 / -1;
  padding: 16px;
  font-weight: bold;
  background: linear-gradient(#632c30, #291719);
  border-color: #b28c68;
}
.menu-art canvas {
  display: block;
  width: 100%;
  max-height: 400px;
  image-rendering: pixelated;
}
.info-card {
  padding: 14px;
  background: #090f0b;
  border: 1px solid #3c4a3d;
  color: #b9c5b8;
  font-size: 11px;
  line-height: 1.8;
}
.info-card b {
  color: #e0d2ad;
}
.danger {
  color: #e18a7e;
}
.pc-hint {
  margin-top: 13px;
  color: #8e9a8e;
  font-size: 9px;
  letter-spacing: 1px;
}
.memorial-home {
  margin-top: 17px;
  padding: 13px 15px 12px;
  border: 1px solid #827554;
  border-left: 3px solid #c9b783;
  background: linear-gradient(120deg, rgba(45,39,26,.8), rgba(12,16,12,.96) 72%);
  color: #d2c9b1;
  box-shadow: inset 0 0 22px rgba(184,159,102,.045);
}
.memorial-home-head { display:flex; gap:10px; align-items:center; margin-bottom:6px; }
.memorial-mark { display:grid; place-items:center; flex:0 0 32px; width:32px; height:32px; border:1px solid #8f805d; color:#ead9ab; font-size:18px; background:#171a13; }
.memorial-home-title { color:#e6d5ac; display:block; font-size:10px; letter-spacing:2.2px; }
.memorial-home-date { display:block; color:#a79b7c; font-size:9px; margin-top:4px; letter-spacing:.5px; }
.memorial-icons { display:flex; gap:6px; flex-wrap:wrap; margin:8px 0; }
.memorial-icons span { padding:4px 7px; color:#d8c99e; background:#171b13; border:1px solid #484533; font-size:9px; letter-spacing:.6px; }
.memorial-home p { margin:8px 0 0; font-size:11px; line-height:1.7; color:#c3c8b9; }
.memorial-home .memorial-signoff { display:block; margin-top:8px; color:#e0d1a9; font-size:10px; letter-spacing:.4px; }
.memorial-panel { width:min(760px,96vw); border-color:#8b7d5b; background:linear-gradient(145deg,rgba(21,23,17,.99),rgba(5,7,6,.99)); }
.memorial-panel .section-title { color:#efe3c5; letter-spacing:.5px; }
.memorial-letter { margin:18px 0; padding:20px clamp(16px,4vw,30px); border-top:1px solid #827554; border-bottom:1px solid #827554; background:linear-gradient(120deg,rgba(49,44,30,.47),rgba(8,11,8,.75)); color:#d3cbb8; font-size:13px; line-height:1.95; }
.memorial-photo-row { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin:16px 0; }
.memorial-photo { min-height:86px; display:flex; flex-direction:column; justify-content:center; align-items:center; gap:8px; padding:10px 5px; border:1px solid #59533e; background:#0b0f0a; color:#cabb95; text-align:center; font-size:10px; letter-spacing:1px; }
.memorial-photo strong { font-size:25px; line-height:1; font-weight:normal; color:#e0d0a6; }
.memorial-note { color:#a9ad9d; font-size:10px; line-height:1.7; }
@media(max-width:760px) { .memorial-photo-row { gap:5px; } .memorial-photo { min-height:73px; font-size:8px; } .memorial-photo strong { font-size:20px; } .memorial-home p { font-size:10px; } }
.section-title {
  margin: 7px 0 12px;
  color: #e8e2ce;
  font-size: clamp(22px, 4vw, 30px);
}
.selection-strip {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 18px 0;
}
.character {
  min-width: 0;
  padding: 12px 8px;
  text-align: center;
  text-transform: none;
  letter-spacing: 0;
  border-color: #475548;
}
.avatar {
  display: flex;
  height: 76px;
  justify-content: center;
  align-items: center;
  margin-bottom: 8px;
}
.avatar canvas {
  width: 68px;
  height: 68px;
  image-rendering: pixelated;
}
.character strong {
  display: block;
  font-size: 11px;
}
.character small {
  display: block;
  margin-top: 6px;
  color: #aeb9ac;
  font-size: 9px;
  line-height: 1.55;
}
.choice-row {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  margin: 12px 0 18px;
}
.choice-row button {
  flex: 1;
  min-width: 140px;
}
.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 13px;
}
.page-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  margin-top: 22px;
}
.page-buttons button {
  min-width: 130px;
}
.credits-lines {
  margin: 18px 0;
  padding: 6px 0 6px 16px;
  border-left: 2px solid #963d40;
  color: #c4cebf;
  line-height: 1.8;
}
.credits-panel {
  background: linear-gradient(145deg, rgba(10, 18, 13, .98), rgba(5, 8, 7, .98));
  border-color: #76664a;
}
.credits-hero {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  margin: 18px 0 22px;
  background: linear-gradient(110deg, #17221a, #0a100c);
  border: 1px solid #485544;
}
.credits-mark {
  display: grid;
  flex: 0 0 58px;
  height: 58px;
  place-items: center;
  border: 2px solid #9b4644;
  background: #160e0e;
  color: #e4c98d;
  font-size: 22px;
  font-weight: 900;
  text-shadow: 2px 2px #4d1b1d;
}
.credits-hero b, .credits-hero span, .credits-hero small {
  display: block;
}
.credits-hero b {
  color: #e8dfc7;
  font-size: 17px;
  letter-spacing: 2px;
}
.credits-hero span {
  margin-top: 5px;
  color: #c5b487;
  font-size: 10px;
  letter-spacing: 1px;
}
.credits-hero small {
  margin-top: 7px;
  color: #96a293;
  font-size: 10px;
}
.credit-name {
  display: inline-block;
  margin-top: 8px;
  color: #f0d7a0;
  font-size: 20px;
  letter-spacing: .5px;
}
.credit-alias {
  color: #b7a57f;
  font-size: 11px;
}
.credits-lines p {
  margin: 11px 0 0;
}
.credits-quote {
  border-color: #65563a;
  color: #e0d2ac;
  font-style: italic;
  line-height: 1.8;
}
.rule-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 9px;
  margin: 17px 0;
}
.rule {
  padding: 11px 12px;
  border: 1px solid #344335;
  background: #0b120d;
  color: #b8c4b7;
  font-size: 11px;
  line-height: 1.65;
}
.rule b {
  display: block;
  margin-bottom: 3px;
  color: #e0d0a5;
  letter-spacing: .5px;
}
.badge {
  display: inline-block;
  padding: 4px 7px;
  margin: 3px 3px 0 0;
  border: 1px solid #695b3d;
  color: #dfcc98;
  font-size: 9px;
  letter-spacing: 1px;
}
#objectivePanel,
#inventoryPanel,
#pausePanel,
#endingPanel,
#radioPanel,
#interviewPanel,
#stationIntakePanel {
  z-index: 9;
}
.station-panel { width:min(1040px,97vw); max-height:95vh; overflow:auto; border-color:#5c6959; background:linear-gradient(155deg,#0c120d,#030504 68%); box-shadow:0 0 70px #000, inset 0 0 40px #090e0a; }
.station-topline { display:flex; justify-content:space-between; gap:12px; align-items:center; padding:9px 11px; margin-bottom:15px; border:1px solid #475445; background:#070b08; color:#a8b79d; font:10px/1.4 monospace; letter-spacing:1.4px; }
.station-alert { color:#d58d7b; }
.station-layout { display:grid; grid-template-columns:minmax(220px,.72fr) minmax(320px,1.28fr); gap:13px; align-items:stretch; }
.station-card { min-width:0; padding:12px; background:#070b08; border:1px solid #374536; }
.station-feed { display:flex; align-items:center; justify-content:space-between; padding:7px 8px; background:#182219; border-bottom:1px solid #55644f; color:#d9d7b9; font:9px/1.4 monospace; letter-spacing:1px; }
.station-lamp { width:7px; height:7px; display:inline-block; border-radius:50%; background:#b3443d; box-shadow:0 0 10px #b3443d; margin-right:5px; }
.station-portrait { position:relative; height:150px; display:flex; align-items:center; justify-content:center; overflow:hidden; background:radial-gradient(ellipse at 50% 36%,#293028 0,#0b100c 53%,#020302 100%); border:1px solid #283428; margin:10px 0; }
.station-portrait::before { content:""; position:absolute; width:100%; height:1px; top:0; background:#6f8372; opacity:.7; animation:stationScan 4.2s linear infinite; }
.station-portrait::after { content:"CAM 04 · LOW-LIGHT CAPTURE"; position:absolute; bottom:7px; left:8px; color:#697a67; font:8px monospace; letter-spacing:1px; }
.station-face { position:relative; width:67px; height:87px; background:#8b8874; border-radius:42% 42% 34% 34%; box-shadow:0 0 17px #c4c09a22; }
.station-face::before { content:""; position:absolute; left:-8px; top:11px; width:83px; height:30px; background:#181b17; clip-path:polygon(0 0,100% 0,87% 37%,63% 22%,40% 43%,12% 27%); }
.station-face::after { content:""; position:absolute; left:11px; top:43px; width:45px; height:5px; background:#24231d; box-shadow:0 12px 0 -1px #6e6b5d; }
.station-portrait.anomaly .station-face { filter:contrast(1.65) brightness(.62); transform:rotate(-2deg) scaleY(1.04); box-shadow:0 0 18px #a824242e; }
.station-portrait.anomaly .station-face::after { height:2px; background:#1a0304; box-shadow:0 11px 0 1px #1a0304; }
.station-name { margin:4px 0 2px; color:#efe5c9; font-size:16px; letter-spacing:1px; }
.station-role { color:#94a18f; font-size:10px; line-height:1.5; margin-bottom:10px; }
.station-doc { padding:9px; border:1px dashed #66715a; background:#101710; color:#c6cfbc; font:10px/1.7 monospace; white-space:pre-wrap; overflow-wrap:anywhere; }
.station-doc strong { color:#e2cc8b; }
.station-status { margin-top:8px; padding:8px; border-left:3px solid #917c4d; background:#100f0a; color:#c7b78a; font-size:10px; line-height:1.5; }
.station-chatlog { display:flex; flex-direction:column; gap:7px; min-height:180px; max-height:34vh; overflow-y:auto; padding:10px; border:1px solid #293528; background:#020403; }
.station-line { max-width:96%; align-self:flex-start; padding:7px 9px; border-left:2px solid #667d5d; background:#101811; color:#d3d8c8; font-size:11px; line-height:1.55; white-space:pre-wrap; overflow-wrap:anywhere; }
.station-line.officer { align-self:flex-end; border-left:0; border-right:2px solid #b69d61; background:#17150e; color:#e4d9bb; }
.station-line.system { max-width:100%; border-left:2px solid #9b3735; background:#100708; color:#d99c94; }
.station-sender { display:block; margin-bottom:3px; font-size:8px; letter-spacing:1px; color:#9eb28f; }
.station-line.officer .station-sender { color:#d4bc80; }
.station-compose { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:6px; margin:7px 0 10px; }
#stationChatInput { min-width:0; width:100%; background:#080e09; border:1px solid #455440; color:#f3efdb; padding:9px; text-transform:none; letter-spacing:0; font-size:11px; }
.station-questions { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:7px; margin:8px 0; }
.station-questions button { min-height:43px; padding:7px 5px; font-size:9px; line-height:1.45; letter-spacing:.3px; }
.station-questions button.checked { border-color:#a7bd86; background:#1b2a1a; color:#dcf0c4; }
.station-decisions { display:grid; grid-template-columns:1fr 1fr; gap:9px; margin:11px 0; }
.station-decisions button { min-height:46px; font-weight:bold; }
.station-decisions [data-station-decision="detain"] { border-color:#98534c; background:linear-gradient(#45201f,#1e0e0e); color:#f0c3b8; }
.station-feedback { min-height:56px; padding:10px; border:1px solid #3a4636; background:#080d09; color:#c3cbb8; font-size:11px; line-height:1.65; }
.station-feedback.good { border-color:#68825c; color:#cbe2b9; }
.station-feedback.bad { border-color:#9a4741; color:#eab3a7; }
.station-score { color:#e4d5a8; font:10px monospace; letter-spacing:1px; }
.station-summary { padding:18px; border:1px solid #4b5947; background:#070b08; line-height:1.8; }
.station-summary h3 { margin-top:0; color:#e7d9b1; }
@keyframes stationScan { 0% { transform:translateY(0);opacity:0; } 5% { opacity:.7; } 95% { opacity:.55; } 100% { transform:translateY(149px);opacity:0; } }
.station-topic-questions { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:6px; margin:8px 0 11px; }
.station-topic-questions button { min-height:37px; padding:7px 6px; font-size:9px; line-height:1.35; letter-spacing:.25px; border-color:#514c3b; color:#d2c59a; background:#15140d; }
.station-topic-questions button.checked { border-color:#8f403b; color:#e5b5aa; background:#210b0c; }
.station-incident { margin:8px 0 12px; padding:9px 11px; border:1px solid #70403c; background:#100607; color:#d8a39b; font:10px/1.55 monospace; letter-spacing:.6px; }
.station-incident.hidden { display:none; }
#stationIntakePanel.breach-mid .station-topline { border-color:#75403a; box-shadow:0 0 19px #9b282522; }
#stationIntakePanel.breach-mid .station-lamp { animation:stationLamp 1.1s steps(2,end) infinite; }
#stationIntakePanel.breach-final .station-portrait { background:radial-gradient(ellipse at 50% 36%,#25090b 0,#080202 57%,#000 100%); border-color:#862d33; }
#stationIntakePanel.breach-final .station-portrait::after { content:'CAM 04 · DOOR EVENT: NONE'; color:#d57b77; }
#stationIntakePanel.breach-final .station-chatlog { border-color:#683035; box-shadow:inset 0 0 24px #3c00051c; }
@keyframes stationLamp { 0%,100%{opacity:1} 48%{opacity:.15} 52%{opacity:.8} }
@media(max-width:720px) { .station-layout { grid-template-columns:1fr; } .station-portrait { height:100px; } .station-chatlog { min-height:115px; max-height:23vh; } .station-questions,.station-topic-questions { grid-template-columns:1fr; } .station-panel { padding:12px; } .station-name { font-size:13px; } }
.evidence-board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 10px;
  margin-top: 12px;
}
.evidence-card {
  padding: 13px;
  background: linear-gradient(135deg, #101a12, #080d0a);
  border: 1px solid #43513e;
  min-width: 0;
}
.evidence-card.studied { border-color: #8d9d69; background: linear-gradient(135deg, #172319, #0b120d); }
.evidence-card.missing { border-color: #76504b; opacity: .82; }
.evidence-card h3 { margin: 0 0 7px; color: #e0d2ad; font-size: 12px; line-height: 1.5; }
.evidence-card p { margin: 7px 0; color: #b9c5b8; font-size: 11px; line-height: 1.65; }
.evidence-card .evidence-meta { color: #8f9a88; font-size: 9px; letter-spacing: 1px; }
.evidence-card button { margin-top: 8px; width: 100%; }
.interview-question { padding: 15px; background: #0a110c; border-left: 3px solid #9b8c60; color: #e0d9c5; font-size: 13px; line-height: 1.8; margin: 14px 0; }
.interview-choices { display: grid; grid-template-columns: 1fr; gap: 9px; }
.interview-choices button { text-align: left; text-transform: none; letter-spacing: .25px; line-height: 1.55; }
.interview-feedback { min-height: 44px; margin-top: 12px; padding: 12px; background: #0a100b; border: 1px solid #394638; color: #c1cbb9; font-size: 12px; line-height: 1.7; }

#interviewPanel {
  z-index: 70;
  background: radial-gradient(ellipse at 24% 40%, rgba(27,17,17,.24), #000 58%, #000 100%);
  backdrop-filter: blur(2px);
}
.witness-frame {
  width: min(1260px, 98vw);
  max-height: 94vh;
  display: grid;
  grid-template-columns: minmax(270px,.86fr) minmax(360px,1.14fr);
  gap: 0;
  overflow: auto;
  border: 1px solid #61564b;
  background: #030403;
  box-shadow: 0 0 0 6px #000b, 0 0 100px #050000, inset 0 0 80px #160608;
  animation: witnessCameraPush 1.5s cubic-bezier(.2,.7,.18,1) both;
}
.witness-camera {
  position: relative;
  min-height: 560px;
  overflow: hidden;
  background: radial-gradient(ellipse at 50% 35%, #1c211b 0, #070907 42%, #000 78%);
  border-right: 1px solid #44382f;
}
.witness-camera::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 4;
  pointer-events: none;
  background: repeating-linear-gradient(0deg, transparent 0 3px, rgba(190,205,184,.045) 4px, transparent 5px 8px), linear-gradient(90deg, rgba(0,0,0,.4), transparent 22% 78%, rgba(0,0,0,.6));
  mix-blend-mode: screen;
}
.witness-camera::after {
  content: 'CAM 02 // LOCAL FEED // AUDIO DOES NOT MATCH LIP MOVEMENT';
  position: absolute;
  z-index: 5;
  left: 12px;
  right: 12px;
  bottom: 12px;
  color: #b3b8a0;
  font: 9px/1.6 Consolas,monospace;
  letter-spacing: 1.2px;
  padding: 7px 8px;
  background: #000b;
  border-left: 2px solid #8d4840;
}
.witness-camera-label {
  position: absolute;
  z-index: 5;
  top: 14px;
  left: 13px;
  color: #bc514a;
  font: bold 10px/1.4 Consolas,monospace;
  letter-spacing: 1.7px;
  text-shadow: 0 0 12px #8d181b;
}
.silas-close-face {
  position: absolute;
  left: 50%;
  top: 13%;
  width: min(76%, 310px);
  height: 66%;
  transform: translateX(-50%) scale(1.04);
  transform-origin: 50% 38%;
  background: radial-gradient(ellipse at 46% 29%, #777665 0, #494b40 22%, #252920 45%, #0b0e0a 72%, #000 100%);
  clip-path: polygon(23% 0,77% 0,95% 18%,91% 49%,83% 75%,67% 100%,34% 100%,16% 75%,7% 48%,6% 19%);
  filter: contrast(1.25) brightness(.68);
  animation: silasSlowZoom 7.7s ease-in-out infinite alternate, silasFaceFlicker 11s steps(1,end) infinite;
}
.silas-close-face::before {
  content: '';
  position: absolute;
  left: -7%; right: -7%; top: 10%; height: 21%;
  background: linear-gradient(180deg,#050605,#171a14 60%,#090a08);
  clip-path: polygon(0 0,100% 0,89% 65%,72% 35%,55% 76%,39% 28%,15% 66%);
}
.silas-eye {
  position: absolute; top: 35%; width: 18%; height: 4%; background: #c9c3a9;
  box-shadow: 0 0 11px 3px #b6a98b55;
}
.silas-eye.left { left: 21%; transform: rotate(5deg); }
.silas-eye.right { right: 21%; transform: rotate(-5deg); }
.silas-mouth {
  position: absolute; left: 32%; top: 59%; width: 37%; height: 10%;
  background: #030403; border-top: 1px solid #a18f7b; transform: skewY(-3deg);
}
.silas-mouth::after {
  content: ''; position:absolute; left:14%; right:9%; top:1px; height:5px;
  background: repeating-linear-gradient(90deg,#c4b8a0 0 5px,#1b1d17 5px 8px); opacity:.7;
}
.silas-neck {
  position: absolute; left: 37%; bottom: 1%; width: 27%; height: 25%;
  background: linear-gradient(90deg,#070807,#282c22 45%,#0b0c0a); z-index:-1;
}
.silas-close-face.unsettled { filter: contrast(1.6) brightness(.52) hue-rotate(-16deg); animation: silasSlowZoom 4.2s ease-in-out infinite alternate, silasFaceFlicker 5.5s steps(1,end) infinite; }
.witness-caption {
  position: absolute; z-index: 6; left: 16px; right: 16px; bottom: 67px; text-align: center;
  padding: 11px 12px; color: #ded6c3; background: #020403e8; border: 1px solid #4d4b3a;
  font: 11px/1.7 Consolas,monospace; min-height: 48px; text-shadow: 0 0 10px #b7a98b33;
}
.witness-dialogue { padding: clamp(18px,3vw,34px); min-width: 0; }
.witness-dialogue .intro { margin-top: 0; }
@keyframes witnessCameraPush { from { opacity:0; transform:scale(1.13); filter:blur(8px); } to { opacity:1; transform:scale(1); filter:blur(0); } }
@keyframes silasSlowZoom { from { transform:translateX(-50%) scale(1.02); } to { transform:translateX(-50%) scale(1.17); } }
@keyframes silasFaceFlicker { 0%,92%,94%,100% { opacity:1; } 93% { opacity:.35; } 95% { opacity:.84; } }
.station-zoom-button { width:100%; margin:4px 0 10px; border-color:#8e4b44; color:#f0c2b7; background:linear-gradient(#351819,#100809); font-size:10px; }
#suspectZoomPanel { z-index: 85; background: radial-gradient(ellipse at 50% 42%, rgba(16,7,8,.35), #000 70%, #000); }
.suspect-zoom-shell {
  width:min(1260px,98vw); max-height:94vh; overflow:auto; display:grid;
  grid-template-columns:minmax(290px,.9fr) minmax(350px,1.1fr);
  background:#020302; border:1px solid #76504b; box-shadow:0 0 0 6px #000c,0 0 100px #310609;
  animation:witnessCameraPush 1.1s cubic-bezier(.12,.68,.2,1) both;
}
.suspect-camera {
  min-height:570px; position:relative; overflow:hidden; background:radial-gradient(ellipse at 50% 32%,#2b2b25 0,#11130f 33%,#030403 71%,#000 100%); border-right:1px solid #493a35;
}
.suspect-camera::before { content:'';position:absolute;inset:0;z-index:4;pointer-events:none;background:repeating-linear-gradient(0deg,transparent 0 3px,rgba(206,211,196,.055) 4px,transparent 5px 9px),linear-gradient(90deg,rgba(0,0,0,.55),transparent 25% 75%,rgba(0,0,0,.55)); }
.suspect-camera-label { position:absolute;z-index:5;top:14px;left:14px;color:#d07b6e;font:bold 10px/1.5 Consolas,monospace;letter-spacing:1.6px; }
.suspect-camera-status { position:absolute;z-index:5;left:13px;right:13px;bottom:13px;padding:8px;background:#000c;color:#c2b6a2;border-left:2px solid #a53e42;font:9px/1.6 Consolas,monospace;letter-spacing:1px; }
.suspect-zoom-figure { position:absolute;left:50%;top:12%;width:min(88%,350px);height:75%;transform:translateX(-50%);filter:contrast(1.35) brightness(.68);animation:suspectSlowPush 5.4s ease-in-out infinite alternate; }
.suspect-zoom-figure .zoom-head { position:absolute;left:25%;top:4%;width:50%;height:48%;border-radius:42% 42% 35% 35%;background:radial-gradient(ellipse at 40% 25%,#888573,#4a4d40 45%,#151811 78%,#030403);clip-path:polygon(17% 0,82% 0,100% 28%,89% 74%,64% 100%,35% 100%,11% 72%,0 27%); }
.suspect-zoom-figure .zoom-hair { position:absolute;left:20%;top:0;width:60%;height:26%;background:#080a08;clip-path:polygon(0 0,100% 0,90% 70%,74% 45%,57% 82%,39% 45%,12% 78%); }
.suspect-zoom-figure .zoom-eyes { position:absolute;left:33%;top:24%;width:35%;height:4%;background:#d5c7aa;box-shadow:0 0 8px 3px #b42d31; }
.suspect-zoom-figure .zoom-mouth { position:absolute;left:37%;top:42%;width:27%;height:7%;background:#030302;border-top:1px solid #aa8e79;clip-path:polygon(0 0,100% 0,87% 100%,18% 70%); }
.suspect-zoom-figure .zoom-body { position:absolute;left:7%;right:7%;top:44%;bottom:0;background:linear-gradient(90deg,#030403,#182018 30%,#070907 54%,#1a1c17 74%,#030403);clip-path:polygon(30% 0,70% 0,90% 18%,100% 100%,0 100%,11% 18%); }
.suspect-zoom-figure.anomaly { filter:contrast(1.8) brightness(.42) sepia(.25) hue-rotate(-22deg); animation:suspectSlowPush 2.8s ease-in-out infinite alternate,silasFaceFlicker 4.5s steps(1,end) infinite; }
@keyframes suspectSlowPush { from { transform:translateX(-50%) scale(1.01); } to { transform:translateX(-50%) scale(1.22); } }
.suspect-dialogue { min-width:0;padding:clamp(18px,3vw,34px); }
.suspect-dialogue .interview-question { min-height:92px; }
.suspect-zoom-choices { display:grid;grid-template-columns:1fr;gap:8px;margin:13px 0; }
.suspect-zoom-choices button { text-align:left;text-transform:none;letter-spacing:.2px;font-size:11px;line-height:1.5; }
.suspect-zoom-response { min-height:80px;padding:12px;border:1px solid #533b37;background:#080505;color:#d5c8b9;font:11px/1.7 Consolas,monospace; }
@media(max-width:760px) {
  .witness-frame,.suspect-zoom-shell { grid-template-columns:1fr; }
  .witness-camera,.suspect-camera { min-height:260px;height:30vh; }
  .silas-close-face { top:4%;height:85%;width:min(46%,220px); }
  .suspect-zoom-figure { top:3%;height:92%;width:min(48%,230px); }
  .witness-caption { bottom:49px;font-size:9px; }
}
@media (prefers-reduced-motion: reduce) {
  .witness-frame,.silas-close-face,.suspect-zoom-shell,.suspect-zoom-figure { animation:none; }
}

.task-row {
  display: flex;
  gap: 10px;
  padding: 10px 2px;
  border-bottom: 1px solid #263328;
  color: #c3cbbb;
  font-size: 12px;
  line-height: 1.6;
}
.task-mark {
  flex: 0 0 18px;
  color: #d3bb7d;
}
.task-row.done .task-mark {
  color: #9cbf85;
}
.task-row.done .task-copy {
  color: #829283;
  text-decoration: line-through;
}
.inventory-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin: 18px 0;
}
.inventory-slot {
  min-height: 85px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 7px;
  border: 1px solid #455243;
  background: #0b120e;
  color: #d1d6c7;
  text-align: center;
  font-size: 10px;
}
.inventory-slot span {
  color: #8f9b8d;
  font-size: 18px;
}

#partnerChat {
  position:fixed;
  z-index:8;
  top:14px;
  left:14px;
  width:min(310px,34vw);
  max-height:36vh;
  overflow:hidden;
  display:none;
  flex-direction:column;
  color:#e7ebdf;
  background:linear-gradient(180deg,rgba(5,12,10,.98),rgba(8,15,12,.96));
  border:1px solid #82927c;
  box-shadow:0 5px 24px #000b,inset 0 0 0 1px #17231a;
  text-shadow:0 1px 3px #000;
  pointer-events:auto;
}
body.prologue-mode.prologue-drive #partnerChat,
body.prologue-mode.prologue-arrival #partnerChat,
body.game-active:not(.prologue-mode) #partnerChat { display:flex; }
body.game-active:not(.prologue-mode) #partnerChat { top:142px; }
.partner-head {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:8px;
  padding:8px 10px;
  background:#1b2a20;
  border-bottom:1px solid #4e624d;
  color:#d7d8bc;
  font-size:10px;
  letter-spacing:1px;
}
.partner-live { color:#9fc18c; white-space:nowrap; }
.partner-live::before { content:"● "; color:#8cc77c; }
#partnerMessages { padding:7px 8px 8px; display:flex; flex-direction:column; gap:6px; max-height:calc(36vh - 84px); min-height:58px; overflow-y:auto; overflow-x:hidden; scrollbar-width:thin; flex:1 1 auto; }
.partner-message { max-width:96%; padding:6px 8px; font-size:10px; line-height:1.45; white-space:pre-wrap; overflow-wrap:anywhere; background:#151e18; border-left:2px solid #8ca47e; }
.partner-message.outgoing { align-self:flex-end; background:#20231b; border-left:0; border-right:2px solid #c5ae70; color:#e1d8bc; }
.partner-sender { display:block; margin-bottom:2px; color:#a7c19a; font-size:8px; letter-spacing:.7px; }
.partner-message.outgoing .partner-sender { color:#d2b979; }
.partner-message.unknown { align-self:center; width:100%; max-width:100%; color:#f0c7c4; background:repeating-linear-gradient(180deg,#211011 0 3px,#120a0b 3px 6px); border:1px solid #8d363b; box-shadow:inset 0 0 18px #740e1833,0 0 12px #8c1e2833; animation:unknownSignal .22s steps(2,end) 5; }
.partner-message.unknown .partner-sender { color:#ff7777; }
@keyframes unknownSignal { 0%{transform:translateX(0);opacity:1} 25%{transform:translateX(2px);opacity:.72} 50%{transform:translateX(-2px);opacity:1} 75%{transform:translateX(1px);opacity:.82} 100%{transform:translateX(0);opacity:1} }
#partnerComposer { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:5px; padding:6px; border-top:1px solid #485847; background:#080e0b; pointer-events:auto; }
#partnerInput { display:block; width:100%; min-width:0; padding:8px 9px; border:1px solid #4a5b4a; border-radius:0; background:#111a13; color:#f1f0df; font-size:11px; line-height:1.2; letter-spacing:0; text-transform:none; user-select:text; -webkit-user-select:text; pointer-events:auto; }
#partnerInput::placeholder { color:#849183; opacity:1; }
#partnerInput:focus { outline:1px solid #d0b773; border-color:#d0b773; }
#partnerSend { padding:7px 9px; font-size:9px; letter-spacing:.5px; white-space:nowrap; }
.partner-hint { padding:0 8px 5px; color:#788676; font-size:8px; line-height:1.3; }
#driveLaneHUD {
  display:none;
  position:fixed;
  z-index:4;
  top:84px;
  right:14px;
  width:min(250px,31vw);
  padding:9px 10px 10px;
  color:#e5eadc;
  background:rgba(4,9,7,.91);
  border:1px solid #77846b;
  box-shadow:0 5px 22px #0009;
  pointer-events:none;
}
body.prologue-mode.prologue-drive #driveLaneHUD { display:block; }
.drive-lane-kicker { font-size:9px; color:#b0c3a2; letter-spacing:1.2px; }
#driveLaneLabel { margin:5px 0 7px; font-size:12px; font-weight:bold; color:#e3dfc3; }
.lane-track { position:relative; height:24px; display:grid; grid-template-columns:1fr 12px 1fr; gap:2px; border:1px solid #566354; background:#121812; overflow:hidden; }
.lane-track .lane-oncoming { background:repeating-linear-gradient(135deg,#242c2b 0 6px,#303a36 6px 12px); }
.lane-track .lane-center { z-index:1; background:linear-gradient(90deg,#a7904e 0 30%,#e2cb78 30% 42%,#31301f 42% 58%,#e2cb78 58% 70%,#a7904e 70%); }
.lane-track .lane-travel { background:repeating-linear-gradient(135deg,#1f2e22 0 6px,#304331 6px 12px); }
#laneMarker { position:absolute; z-index:2; left:75%; top:1px; width:4px; height:20px; background:#fff4bc; border:1px solid #151711; box-shadow:0 0 8px #fff2ab; transform:translateX(-50%); }
.lane-labels { display:flex; justify-content:space-between; margin-top:4px; color:#9da99a; font-size:8px; }
#laneAdvice { margin-top:6px; color:#c4cebd; font-size:9px; line-height:1.4; }
@media(max-width:700px) {
  #partnerChat { width:min(270px,66vw); max-height:37vh; top:8px; left:8px; }
  body.game-active:not(.prologue-mode) #partnerChat { top:128px; }
  #partnerMessages { max-height:calc(37vh - 84px); min-height:44px; }
  #partnerInput { padding:7px 6px; font-size:10px; }
  #partnerSend { padding:7px 6px; font-size:8px; }
  .partner-head { font-size:9px; padding:6px 7px; }
  .partner-message { font-size:9px; padding:5px 6px; }
  #driveLaneHUD { top:8px; right:8px; width:min(195px,40vw); padding:7px; }
  .drive-lane-kicker { font-size:8px; }
  #driveLaneLabel { font-size:10px; }
  #laneAdvice { font-size:8px; }
}

#touchControls {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 3;
  pointer-events: none;
}
#dpad {
  position: absolute;
  left: 16px;
  bottom: 18px;
  width: 144px;
  height: 144px;
  pointer-events: auto;
}
#dpad button {
  position: absolute;
  width: 45px;
  height: 45px;
  padding: 0;
  background: #101911d9;
  border-color: #7f8a78;
  font-size: 19px;
  touch-action: none;
}
#up {
  left: 49px;
  top: 0;
}
#down {
  left: 49px;
  bottom: 0;
}
#left {
  left: 0;
  top: 49px;
}
#right {
  right: 0;
  top: 49px;
}
#touchActions {
  position: absolute;
  right: 15px;
  bottom: 18px;
  display: grid;
  grid-template-columns: repeat(2, 61px);
  gap: 8px;
  pointer-events: auto;
}
#touchActions button {
  width: 61px;
  height: 49px;
  padding: 2px;
  background: #101911e8;
  border-color: #7f8a78;
  font-size: 9px;
  touch-action: none;
}
body.game-active.mobile-mode #touchControls {
  display: block;
}
body.game-active.mobile-mode #bottom {
  bottom: 178px;
}
body.game-active.mobile-mode #minimap {
  width: 85px;
  height: 85px;
}
#voiceSubtitle {
  position:fixed;
  z-index:14;
  left:50%;
  bottom:clamp(78px,13vh,150px);
  width:min(620px,90vw);
  transform:translateX(-50%) translateY(8px);
  display:none;
  padding:11px 15px 12px;
  text-align:center;
  color:#d5d9ca;
  background:linear-gradient(90deg,rgba(4,8,6,.15),rgba(3,5,4,.94) 18%,rgba(3,5,4,.94) 82%,rgba(4,8,6,.15));
  border-top:1px solid #52604e;
  border-bottom:1px solid #52604e;
  text-shadow:0 2px 5px #000;
  pointer-events:none;
  opacity:0;
  transition:opacity .22s,transform .22s;
}
#voiceSubtitle.active { display:block; opacity:1; transform:translateX(-50%) translateY(0); animation:whisperFlicker .14s steps(2,end) 3; }
#voiceWho { display:block; margin-bottom:5px; color:#b79a76; font-size:9px; letter-spacing:2px; }
#voiceWords { font-size:clamp(11px,1.6vw,15px); letter-spacing:1.1px; line-height:1.5; font-style:italic; }
#voiceSubtitle.left #voiceWho { color:#a6bc9b; text-align:left; }
#voiceSubtitle.right #voiceWho { color:#ad8e8e; text-align:right; }
@keyframes whisperFlicker { 0%,100% { filter:none; } 50% { filter:blur(.65px); opacity:.62; } }
@media(max-width:700px) { #voiceSubtitle { bottom:170px; width:94vw; padding:8px 10px; } #voiceWords { font-size:10px; } }
#damageFlash {
  position: fixed;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  opacity: 0;
  background: radial-gradient(ellipse, transparent 35%, rgba(155, 16, 22, .55));
}
#interactNotice {
  position: fixed;
  left: 50%;
  bottom: 18%;
  z-index: 2;
  transform: translateX(-50%);
  color: #e7d5a1;
  text-shadow: 0 2px 5px black;
  font-size: 10px;
  letter-spacing: 1px;
  pointer-events: none;
}
@media (max-width: 700px) {
  .menu-layout {
    grid-template-columns: 1fr;
    gap: 5px;
  }
  .menu-art {
    display: none;
  }
  .logo {
    margin-top: 13px;
  }
  .menu-actions {
    margin-top: 13px;
  }
  .panel {
    padding: 23px;
  }
  .intro {
    font-size: 11px;
  }
  .selection-strip {
    gap: 5px;
  }
  .character {
    padding: 8px 4px;
  }
  .avatar {
    height: 55px;
  }
  .avatar canvas {
    width: 51px;
    height: 51px;
  }
  .two-col,
  .rule-list {
    grid-template-columns: 1fr;
  }
  .hudbox {
    padding: 7px 8px;
    font-size: 9px;
  }
  .hudbox b {
    font-size: 9px;
  }
  #topbar {
    top: 7px;
    left: 7px;
    right: 7px;
  }
  #bottom {
    left: 7px;
    right: 7px;
    bottom: 7px;
  }
  #minimap {
    width: 78px;
    height: 78px;
  }
  #survivorLocator { top:calc(136px + 37vh + 8px); width:min(270px,88vw); padding:7px 9px; }
  #survivorLocator .locator-main { font-size:10px; }
  #survivorLocator .locator-sub { font-size:9px; }
  .menu-actions button {
    padding: 11px 6px;
    font-size: 10px;
  }
  .inventory-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
#survivalActions { position:fixed; z-index:5; right:14px; top:145px; display:flex; flex-direction:column; gap:6px; width:126px; pointer-events:auto; }
#survivalActions button { width:100%; padding:8px 7px; text-align:left; border-color:#5c6e56; background:rgba(4,9,6,.94); color:#d9dfc9; font: bold 9px/1.2 monospace; letter-spacing:.7px; box-shadow:0 3px 13px #0009; }
#survivalActions button:disabled { opacity:.38; border-color:#383d35; }
#survivalActions #screamAction { border-color:#834642; color:#e6b5ae; }
#survivalActions #helpAction { border-color:#607c70; color:#b8d2c4; }
#survivalStatus { display:block; padding:6px; border:1px solid #334033; background:#030504eF; color:#9fac97; font:8px/1.45 monospace; text-align:center; letter-spacing:.3px; }
@media(max-width:700px) { #survivalActions { top:auto; right:10px; bottom:180px; width:84px; gap:4px; } #survivalActions button { padding:7px 4px; font-size:8px; } #survivalStatus { font-size:7px; padding:4px 2px; } }

#partnerChat.radio-silenced{filter:grayscale(1) brightness(.58);border-color:#803c40!important;box-shadow:0 0 24px #c01a2622}
#partnerChat.radio-silenced .partner-live{color:#e46b70}
#huntBanner{position:fixed;z-index:48;top:18px;left:50%;transform:translateX(-50%);width:min(560px,88vw);display:none;pointer-events:none;border:1px solid #8d3537;background:linear-gradient(90deg,rgba(8,2,3,.98),rgba(27,4,6,.95),rgba(8,2,3,.98));box-shadow:0 0 32px #9b101c40,inset 0 0 20px #6f0b1428;padding:10px 15px;text-align:center;color:#f1d6ca;letter-spacing:1.2px;font: bold 11px/1.45 monospace;text-shadow:0 0 8px #bb2626;animation:huntPulse .9s steps(2,end) infinite}
body.hunting #survivorLocator{opacity:0}
#huntBanner.active{display:block}
#huntBanner small{display:block;color:#c18d8d;font-size:9px;font-weight:normal;letter-spacing:1.4px;margin-top:4px}
@keyframes huntPulse{0%,100%{border-color:#6d292d;filter:brightness(.8)}50%{border-color:#e14e4e;filter:brightness(1.18)}}
#radioBreachPanel{z-index:150;background:radial-gradient(ellipse at 50% 28%,rgba(32,7,9,.66),#000 74%,#000)}
.radio-breach-shell{width:min(760px,94vw);max-height:92vh;overflow:auto;padding:clamp(17px,3vw,32px);border:1px solid #8e3f41;background:linear-gradient(180deg,rgba(12,5,6,.99),rgba(2,3,3,.99));box-shadow:0 0 0 1px #2d1514,0 0 70px #b0131f2c;position:relative}
.radio-breach-shell:before{content:'';position:absolute;inset:0;pointer-events:none;background:repeating-linear-gradient(0deg,transparent 0 3px,#e8d5c205 4px 5px);mix-blend-mode:screen}
.radio-breach-top{display:flex;align-items:center;justify-content:space-between;gap:12px;border-bottom:1px solid #442326;padding-bottom:10px;color:#d18c87;font-size:10px;letter-spacing:1.8px}
.radio-breach-signal{display:inline-flex;align-items:center;gap:6px;color:#f07973}
.radio-breach-dot{width:7px;height:7px;border-radius:50%;background:#ec3b44;box-shadow:0 0 13px #f22;animation:huntPulse .8s steps(2,end) infinite}
.radio-breach-title{font-size:clamp(22px,4vw,34px);line-height:1.05;letter-spacing:2px;color:#f0e2ce;margin:19px 0 12px;text-shadow:0 0 20px #9b20254a}
.radio-breach-copy{font-size:13px;color:#b9b5a4;line-height:1.8;max-width:66ch}
.radio-breach-transcript{white-space:pre-line;padding:14px;margin:17px 0;background:#020303;border:1px solid #2d2822;color:#c9c5b3;line-height:1.7;font-size:12px}
.radio-breach-choices{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin-top:16px}
.radio-breach-choices button{min-height:88px;text-align:left;white-space:normal;line-height:1.5;font-size:10px;letter-spacing:.6px;border-color:#4d5142;background:linear-gradient(180deg,#171b16,#080a08);padding:11px}
.radio-breach-choices button:first-child{border-color:#816c3f}
.radio-breach-choices button:last-child{border-color:#7b3436}
.radio-breach-foot{margin-top:13px;color:#736c60;font-size:9px;letter-spacing:1px}
#realityPulse{position:fixed;inset:0;z-index:29;pointer-events:none;display:none;background:linear-gradient(90deg,rgba(25,0,4,.16),transparent 16%,transparent 84%,rgba(25,0,4,.16));mix-blend-mode:screen}
#realityPulse.active{display:block;animation:realityPulse .22s steps(2,end) infinite}
@keyframes realityPulse{0%{opacity:.17;clip-path:inset(0 0 90% 0)}25%{opacity:.55;clip-path:inset(26% 0 62% 0)}50%{opacity:.12;clip-path:inset(58% 0 28% 0)}75%{opacity:.44;clip-path:inset(84% 0 8% 0)}100%{opacity:.2;clip-path:inset(10% 0 80% 0)}}
@media(max-width:650px){#huntBanner{top:8px;font-size:9px;padding:8px 9px;max-width:94vw}#huntBanner small{font-size:8px}.radio-breach-choices{grid-template-columns:1fr}.radio-breach-choices button{min-height:56px}}
#accountPanel{z-index:220;background:rgba(0,0,0,.96);backdrop-filter:blur(10px)}
.account-panel{width:min(930px,95vw);max-height:92vh;overflow:auto;border-color:#53664e;background:linear-gradient(180deg,#0c120d,#030504);box-shadow:0 0 60px #000,0 0 30px #8a25251a}
.account-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:14px 0}
.account-card{min-width:0;padding:14px;border:1px solid #354432;background:#070b08}
.account-card h3{margin:0 0 10px;color:#d9cba3;font-size:12px;letter-spacing:1.2px}
.account-field{display:grid;gap:5px;margin:9px 0;color:#aebaa8;font:10px monospace;letter-spacing:.4px}
.account-field input,.account-field select{width:100%;min-width:0;padding:10px;border:1px solid #3d4a39;background:#020403;color:#eee8d6;font:12px monospace;border-radius:3px}
.account-actions{display:flex;flex-wrap:wrap;gap:7px;margin-top:10px}
.account-actions button{flex:1 1 115px;min-height:38px;font-size:10px;padding:8px}
.account-status{min-height:42px;padding:10px;border:1px solid #3d4937;background:#020403;color:#b9c5b2;font:11px/1.6 monospace;white-space:pre-wrap;overflow-wrap:anywhere}
.account-status.error{color:#ffb8ad;border-color:#733a38}.account-status.good{color:#c9e9b3;border-color:#536e43}
.account-list{display:grid;gap:7px;max-height:220px;overflow:auto;margin-top:8px}
.account-row{padding:9px;border:1px solid #293328;background:#050705;color:#c5cdbd;font:10px/1.6 monospace;overflow-wrap:anywhere}
.account-row strong{color:#e2d3ab}
.account-role{display:inline-block;padding:4px 7px;border:1px solid #56694b;color:#caddad;font:9px monospace;letter-spacing:1px}
@media(max-width:720px){.account-grid{grid-template-columns:1fr}.account-panel{padding:14px}.account-actions button{flex-basis:100px}}

</style>
</head>
<body>
<canvas id="game"></canvas>
<div id="partnerChat" aria-label="Partner officer radio chat">
  <div class="partner-head"><span id="partnerTitle">SECURE OFFICER CHAT</span><span class="partner-live">LINK ACTIVE</span></div>
  <div id="partnerMessages" aria-live="polite" aria-relevant="additions text"></div>
  <form id="partnerComposer" autocomplete="off">
    <input id="partnerInput" type="text" maxlength="180" placeholder="Message your partner…" aria-label="Type a message to the other officer" autocomplete="off" spellcheck="false">
    <button id="partnerSend" type="submit">SEND ↗</button>
  </form>
  <div class="partner-hint">ENTER TO SEND · SECURE CHANNEL</div>
</div>
<div id="driveLaneHUD" aria-label="Driving lane indicator">
  <div class="drive-lane-kicker">FIELD MOVEMENT · OBJECTIVE GUIDE</div>
  <div id="driveLaneLabel">RIGHT / TRAVEL LANE</div>
  <div class="lane-track"><div class="lane-oncoming"></div><div class="lane-center"></div><div class="lane-travel"></div><div id="laneMarker"></div></div>
  <div class="lane-labels"><span>ONCOMING</span><span>DOUBLE YELLOW</span><span>YOUR LANE</span></div>
  <div id="laneAdvice">Keep to the right of the double yellow lines.</div>
</div>
<div id="damageFlash"></div>
<div id="voiceSubtitle" aria-live="polite" aria-atomic="true"><span id="voiceWho">UNKNOWN TRANSMISSION</span><span id="voiceWords"></span></div>
<div id="hud">
  <div id="topbar">
    <div class="hudbox">
      <b>FLORIDA STATE PATROL</b>
      <div class="micro">CASE FS-07 / NIGHT SHIFT</div>
      <div id="health">CONDITION: STABLE</div>
      <div id="healthbar"><div id="healthfill"></div></div>
      <div class="micro">STAMINA</div>
      <div id="staminabar"><div id="staminafill"></div></div>
    </div>
    <div class="hudbox">
      <b>ACTIVE CASE</b>
      <div id="objective">Locate the abandoned checkpoint.</div>
      <div id="status">RADIO: STANDBY</div>
      <div class="micro">OFFICER <span id="officerName">REYES</span> · <span id="timeReadout">02:17 AM</span></div>
    </div>
  </div>
  <div id="survivalActions" aria-label="Survival actions">
    <button id="hideAction" type="button" title="Hide in nearby cover (C)">C · HIDE</button>
    <button id="screamAction" type="button" title="Scream to stagger nearby enemies but attract the Smiler (G)">G · SCREAM</button>
    <button id="helpAction" type="button" title="Request a short radio assist (H)">H · HELP</button>
    <span id="survivalStatus">RUN · HIDE · SCREAM · ASK FOR HELP</span>
  </div>
  <div id="bottom">
    <div class="hudbox">
      <div id="prompt">WASD move · Shift sprint · E investigate · F flashlight</div>
      <div class="micro">AMMO <span id="ammo">6</span>/<span id="reserve">24</span> · EVIDENCE <span id="evidence">0/5</span> · SURVIVORS <span id="survivors">0/2</span> · LIGHT <span id="battery">100%</span></div>
    </div>
    <canvas id="minimap" width="132" height="132"></canvas>
  </div>
  <div id="survivorLocator" aria-live="polite">
    <div class="locator-kicker">SEARCH AND RESCUE TRACKER</div>
    <div id="survivorLocatorMain" class="locator-main">SIGNAL SEARCH INITIALIZING</div>
    <div id="survivorLocatorSub" class="locator-sub">Follow the highlighted marker.</div>
  </div>
  <button id="objectiveToggle">CASE FILE [J]</button>
</div>
<div id="touchControls">
  <div id="dpad">
    <button id="up" aria-label="Move up">▲</button>
    <button id="left" aria-label="Move left">◀</button>
    <button id="right" aria-label="Move right">▶</button>
    <button id="down" aria-label="Move down">▼</button>
  </div>
  <div id="touchActions">
    <button id="touchInteract">SEARCH</button>
    <button id="touchShoot">FIRE</button>
    <button id="touchLight">LIGHT</button>
    <button id="touchReload">RELOAD</button>
    <button id="touchRun">SPRINT</button>
    <button id="touchBag">BAG</button>
  </div>
</div>
<div id="toast"></div>
<div id="interactNotice"></div>
<div id="disclaimerPanel" class="overlay">
  <div class="panel">
    <div class="kicker">Before you answer the call</div>
    <h2 class="section-title">Horror & privacy disclaimer</h2>
    <div class="disclaimer-callout"><b>CONTENT WARNING</b><br>Florida Shadows contains sudden visual jumpscares, distorted faces, flashing red/blue lights, unsettling sounds, simulated injuries, and themes of stalking, death, and isolation. Play at a comfortable volume and take a break if needed.</div>
    <p class="intro">Some scripted scares pretend to reveal a character's personnel file, address, or other private records. These are fictional story effects. They use only the selected in-game officer name and invented text.</p>
    <p class="intro"><b>Privacy:</b> This game does not ask for, access, collect, store, or transmit your real name, home address, contacts, camera, microphone, or precise location. Do not enter real private information into any game field or message.</p>
    <label class="disclaimer-choice"><input id="enablePersonalScares" type="checkbox" checked><span>Enable fictional “personal file” jumpscares. Uncheck this to disable those specific scares; other horror elements remain.</span></label>
    <label class="disclaimer-choice"><input id="enableVoiceWhispers" type="checkbox" checked><span>Enable eerie synthesized whispers and false radio transmissions. These use fictional dialogue only. You can turn them off here.</span></label>
    <div class="page-buttons"><button id="dismissDisclaimer">I understand — continue</button></div>
  </div>
</div>
<div id="personalScare" aria-hidden="true">
  <div class="scare-face"><i class="scare-eye left"></i><i class="scare-eye right"></i><i class="scare-nose"></i><i class="scare-mouth"></i></div>
  <div class="scare-entity"><i class="entity-head"></i><i class="entity-eyes"></i><i class="entity-body"></i><i class="entity-arm left"></i><i class="entity-arm right"></i></div>
  <div class="scare-copy"><h2 id="scareTitle">PERSONNEL RECORD OPENED</h2><pre id="scareMessage"></pre><small id="scareStamp">FILE FS-07 // CONNECTION UNKNOWN</small></div>
</div>
<div id="menu" class="overlay">
  <div class="panel">
    <div class="menu-layout">
      <div>
        <div class="kicker">A pixelated detective horror</div>
        <h1 class="logo">FLORIDA<br><span>SHADOWS</span></h1>
        <div class="subtitle">STATE TROOPER HORROR FILES</div>
        <p class="intro">A missing deputy. A sealed police station. Six visitors on camera and seven sets of footsteps. Something in the marsh has learned the shape of your voice.</p>
        <div class="menu-actions">
          <button id="start">▶ Begin patrol</button>
          <button id="accountBtn">Account / Cloud Saves</button>
          <button id="characterBtn">Choose character</button>
          <button id="controlsBtn">Control mode</button>
          <button id="howBtn">How to play</button>
          <button id="creditsBtn">Credits</button>
          <button id="disclaimerBtn">Horror & privacy disclaimer</button>
        </div>
        <section class="memorial-home" aria-label="In loving memory of Yumi's grandfather">
          <div class="memorial-home-head"><span class="memorial-mark" aria-hidden="true">✦</span><div><strong class="memorial-home-title">IN LOVING MEMORY</strong><small class="memorial-home-date">Yumi’s grandfather · October 16, 2026</small></div></div>
          <div class="memorial-icons" aria-label="His loves"><span>✈ PLANES</span><span>▰ CARS</span><span>▣ PHOTOGRAPHY</span></div>
          <p>He was a great man who lived a long, full life. His passing came suddenly in the early morning, but the things he loved and the memories he leaves behind will continue to matter. May the journeys he admired, the photographs he treasured, and the stories he shared bring comfort to everyone who loves him.</p>
          <span class="memorial-signoff">With heartfelt sympathy to Yumi and her family. May he rest in peace.</span>
        </section>
        <div class="pc-hint">THE SEVENTH ARRIVAL · SCREAM JAM 2026 · HEADPHONES RECOMMENDED</div>
      </div>
      <div class="menu-art">
        <canvas id="artCanvas" width="320" height="390"></canvas>
        <div class="info-card"><b>INCIDENT REPORT / 02:17 AM</b><br>Last transmission: “It's standing between the trees.”<br><span class="danger">UNIT 14 — SIGNAL LOST</span></div>
      </div>
    </div>
  </div>
</div>
<div id="accountPanel" class="overlay hidden" aria-label="Account and cloud data">
  <div class="panel account-panel">
    <div class="kicker">MongoDB cloud profile</div>
    <h2 class="section-title">Account, Saves & Records</h2>
    <p class="intro">Create a player account or sign in to keep progress, achievements, and completed-run scores across devices. Staff access is assigned by the server environment; it cannot be selected in this form.</p>
    <div id="cloudStatus" class="account-status">Checking database availability…</div>
    <div class="account-grid">
      <section class="account-card">
        <h3>ACCOUNT ACCESS</h3>
        <form id="accountForm" autocomplete="on">
          <label class="account-field">USERNAME<input id="accountUsername" name="username" maxlength="24" minlength="3" autocomplete="username" placeholder="Enter username" required></label>
          <label class="account-field">PASSWORD<input id="accountPassword" name="password" type="password" maxlength="128" autocomplete="current-password" placeholder="Enter password" required></label>
          <div class="account-actions"><button id="accountLogin" type="submit">Sign in</button><button id="accountRegister" type="button">Create player account</button><button id="accountLogout" type="button" class="hidden">Sign out</button></div>
        </form>
        <div id="accountIdentity" class="account-row">Not signed in.</div>
        <div id="staffOverview" class="account-row hidden"></div>
        <div class="account-actions"><button id="refreshStaffOverview" type="button" class="hidden">Refresh staff overview</button></div>
      </section>
      <section class="account-card">
        <h3>CLOUD SAVE SLOTS</h3>
        <label class="account-field">SAVE SLOT<select id="cloudSaveSlot"><option value="slot-1">Slot 1</option><option value="slot-2">Slot 2</option><option value="slot-3">Slot 3</option></select></label>
        <div class="account-actions"><button id="cloudSaveButton" type="button">Save current progress</button><button id="cloudLoadButton" type="button">Load selected save</button><button id="cloudRefreshSaves" type="button">Refresh slots</button></div>
        <div id="cloudSaveList" class="account-list"><div class="account-row">Sign in to view cloud saves.</div></div>
      </section>
      <section class="account-card">
        <h3>ACHIEVEMENTS</h3>
        <div id="cloudAchievementList" class="account-list"><div class="account-row">Sign in to sync achievements.</div></div>
      </section>
      <section class="account-card">
        <h3>GLOBAL LEADERBOARD</h3>
        <div id="cloudLeaderboardList" class="account-list"><div class="account-row">Connect MongoDB to load leaderboard entries.</div></div>
        <div class="account-actions"><button id="cloudRefreshLeaderboard" type="button">Refresh leaderboard</button></div>
      </section>
    </div>
    <div class="info-card">Privacy: passwords are hashed before storage. MongoDB connection details and staff credentials are read from environment variables and are never sent to the browser.</div>
    <div class="page-buttons"><button id="backAccount">Return</button></div>
  </div>
</div>
<div id="characterPanel" class="overlay hidden">
  <div class="panel">
    <div class="kicker">Personnel records</div>
    <h2 class="section-title">Choose your officer</h2>
    <p class="intro">Choose one playable lead: one boy officer or one girl officer. Your choice changes movement, resilience, and starting equipment.</p>
    <div class="selection-strip">
      <button class="character selected" data-char="hugo"><div class="avatar"><canvas id="charArt0" width="64" height="64"></canvas></div><strong>BOY · OFFICER HUGO</strong><small>Male playable character<br>Steady aim · Balanced field kit</small></button>
      <button class="character" data-char="yumi"><div class="avatar"><canvas id="charArt1" width="64" height="64"></canvas></div><strong>GIRL · OFFICER YUMI</strong><small>Female playable character<br>Quick response · Longer stamina</small></button>
    </div>
    <div class="info-card" id="characterDetails"><b>BOY · OFFICER HUGO</b><br>Experienced male patrol officer with a balanced field kit.</div>
    <div class="page-buttons"><button id="confirmCharacter">Confirm selection</button><button id="backCharacter">Back to menu</button></div>
  </div>
</div>
<div id="controlsPanel" class="overlay hidden">
  <div class="panel">
    <div class="kicker">Input settings</div>
    <h2 class="section-title">Choose control mode</h2>
    <p class="intro">Choose the controls that match your device. You can switch this later from the main menu.</p>
    <div class="choice-row"><button id="desktopMode" class="selected">Desktop / Laptop</button><button id="mobileMode">Mobile / Touchscreen</button></div>
    <div class="two-col">
      <div class="info-card"><b>DESKTOP</b><br>WASD or arrows to move<br>Shift to sprint<br>E to investigate<br>F to toggle flashlight<br>C to hide in nearby cover<br>G to scream: stagger threats, attract Smiler<br>H to request partner radio pulse<br>R reload · Space/left-click fire<br>J case file · I inventory · Esc pause</div>
      <div class="info-card"><b>MOBILE</b><br>Use the directional pad to move<br>Tap SEARCH to investigate<br>Tap FIRE to shoot<br>Tap LIGHT to use the flashlight<br>Tap SPRINT to run<br>Tap HIDE / SCREAM / HELP on the survival panel<br>Tap BAG for inventory<br>Touch buttons stay visible during play</div>
    </div>
    <div class="page-buttons"><button id="saveControls">Save control mode</button><button id="backControls">Back to menu</button></div>
  </div>
</div>
<div id="howPanel" class="overlay hidden">
  <div class="panel">
    <div class="kicker">Field manual</div>
    <h2 class="section-title">Survive the night shift</h2>
    <div class="rule-list">
      <div class="rule"><b>01 / ANSWER THE CALL</b>Begin on foot at the edge of the woods. Press E or tap to accept dispatch.</div>
      <div class="rule"><b>02 / FOLLOW THE FOOTPATH</b>Move on foot with WASD or arrow keys. Muddy footpaths are kept clear of tree trunks and are drawn on your minimap. Use the flashlight to reveal only the ground directly ahead.</div>
      <div class="rule"><b>03 / YOU ARE ALONE</b>Follow the trail toward the first clues. Your partner is on the radio, but something else has learned their voice.</div>
      <div class="rule"><b>04 / INVESTIGATE</b>Recover at least six physical clues, study six clues with J, and make four distinct cross-reference reports. Interview Silas Venn before extraction can open.</div>
      <div class="rule"><b>04B / SCREEN VISITORS</b>Inside the County Police Station, inspect six visitor IDs, question each one, cross-check the official roster, and make at least five correct admit/detain decisions. Review flagged files after studying four clues.</div>
      <div class="rule"><b>05 / RESCUE</b>Find both missing people. They follow after you help them, and their footsteps attract attention.</div>
      <div class="rule"><b>06 / STAY ALIVE</b>The Smiler learns your habits. Sprinting and constant light make it predict your route. During a hunt, hide only briefly, then break line of sight. A false dispatch may offer a tempting green signal.</div>
      <div class="rule"><b>07 / RUN, HIDE, SCREAM</b>Use C near cover to hide and stay still. G makes a loud scream that can stagger nearby enemies but attracts the Smiler. The Smiler can begin five marked hunt phases; survive by sprinting in bursts, hiding briefly, and using buildings to break sight. H requests a short radio pulse that marks nearby threats, stuns crawlers briefly, and restores a little flashlight battery.</div>
      <div class="rule"><b>08 / BREAK THE SIGNAL</b>Optional: destroy the black signal seals in the County Police Station, Pine Rest Motel, and St. Mercy Chapel. They weaken the mimic network and unlock a true-ending variation.</div>
      <div class="rule"><b>09 / SEARCH BUILDINGS</b>Press E at doors. Search five different buildings, and check rooms again: items may vanish when you look away. Important mission keys remain recoverable.</div>
      <div class="rule"><b>10 / ESCAPE</b>Rescue both survivors, recover and study six clues, generate four distinct cross-reference reports, defend the theory, recover the relay override key, search five buildings, save Silas Venn’s statement, then survive the 30-second extraction defense.</div>
      <div class="rule"><b>11 / A MOMENT OF REMEMBRANCE</b>Optional: inside the County Police Station, look for the framed tribute along the east side of the room. Press E to read it. This quiet memorial is separate from the investigation objectives.</div>
    </div>
    <p class="intro">Search buildings for ammunition, bandages, batteries, and clues. Press J to study collected evidence, compare contradictory details, and submit a supported case theory. Inside the County Police Station, chat with six visitors, inspect their ID cards, compare their explanations with the roster, and decide who should be admitted or detained. At least five decisions must be correct; flagged files can be re-audited after studying four clues. Extraction requires both survivors, six collected and studied clues, four distinct cross-reference reports, the accepted case theory, a corroborated witness statement, a completed intake audit, the relay override key, five different buildings searched, and a 30-second holdout under attack.</p>
    <div class="page-buttons"><button id="backHow">Return to menu</button></div>
  </div>
</div>
<div id="creditsPanel" class="overlay hidden">
  <div class="panel credits-panel">
    <div class="kicker">The people behind the case file</div>
    <h2 class="section-title">Credits & Appreciation</h2>
    <div class="credits-hero">
      <div class="credits-mark">FS</div>
      <div><b>FLORIDA SHADOWS</b><span>STATE TROOPER HORROR FILES</span><small>Pixel horror project · Scream Jam 2026</small></div>
    </div>
    <div class="credits-lines"><b>WITH APPRECIATION TO</b><br><strong class="credit-name">Mayumi Alingarog</strong><br><span class="credit-alias">Also known as Yumi, Mimi, and Yumimi</span><p>To Mayumi Alingarog, my classmate and fellow developer: thank you for being such a helpful, kind, and respectful person. Your support, encouragement, and willingness to share this creative journey mean a lot. Your kindness makes collaboration better, and I am grateful to have you as a classmate and fellow developer.</p><p>This project is a little more special because of the people who offer encouragement along the way. Thank you for being one of them.</p></div>
    <div class="credits-lines"><b>TO EVERYONE WHO PLAYS</b><br>Thank you for stepping into the swamp, investigating the case, and helping bring this horror story to life. Keep exploring, keep creating, and never ignore strange sounds on the radio.</div>
    <div class="info-card credits-quote">“Every mystery leaves a trace. Every crime leaves a shadow. And some shadows are always watching.”</div>
    <div class="page-buttons"><button id="backCredits">Return to menu</button></div>
  </div>
</div>
<div id="memorialPanel" class="overlay hidden" role="dialog" aria-modal="true" aria-labelledby="grandfatherMemorialTitle">
  <div class="panel memorial-panel">
    <div class="kicker">A quiet corner of the County Police Station</div>
    <h2 id="grandfatherMemorialTitle" class="section-title">In Loving Memory</h2>
    <div class="memorial-photo-row" aria-label="A small tribute to his favourite things">
      <div class="memorial-photo"><strong>✈</strong><span>THE PLANES HE LOVED</span></div>
      <div class="memorial-photo"><strong>▰</strong><span>THE CARS HE ADMIRED</span></div>
      <div class="memorial-photo"><strong>▣</strong><span>THE MOMENTS HE SAVED</span></div>
    </div>
    <div class="memorial-letter">
      <p>Dedicated to Yumi’s grandfather, who passed away suddenly in the early morning of October 16, 2026.</p>
      <p>He loved planes, cars, and photographs—the journeys they represented, the details worth noticing, and the moments worth keeping. He lived a long life and was a great man. A sudden goodbye cannot take away the years he lived, the memories he made, or the love that remains.</p>
      <p>May every photograph bring back a story, every passing plane remind those who loved him of the wonder he saw in the world, and every memory make the loss a little gentler with time. May he rest in peace.</p>
    </div>
    <p class="memorial-note">This is a quiet tribute offered with respect and sympathy to Yumi and her family. It is not evidence in the case, and nothing here is meant to turn their loss into a scare.</p>
    <div class="page-buttons"><button id="closeMemorial">Leave the memory in peace</button></div>
  </div>
</div>
<div id="objectivePanel" class="overlay hidden">
  <div class="panel">
    <div class="kicker">Incident FS-07 · Evidence control</div>
    <h2 class="section-title">Investigation case file</h2>
    <p class="intro">Collected evidence is not automatically understood. Study each item, compare its findings, and build a credible timeline before requesting extraction. Some unattended items may disappear.</p>
    <div id="taskList"></div>
    <h3 class="section-title" style="font-size:19px;margin-top:25px">Physical evidence and forensic notes</h3>
    <div id="evidenceProgress" class="info-card">0 clues studied · 6 required</div>
    <div id="evidenceBoard" class="evidence-board"></div>
    <div class="page-buttons"><button id="compareEvidence">Compare studied clues</button></div>
    <div id="comparisonReport" class="info-card">Study at least two items, then compare them for contradictions. Four distinct reports are required to prove the timeline.</div>
    <h3 class="section-title" style="font-size:19px;margin-top:25px">Choose your case theory</h3>
    <p class="intro">A theory must explain the evidence, not just sound frightening. The dispatch log and radio recording contain an important contradiction.</p>
    <div id="theoryChoices" class="interview-choices">
      <button type="button" data-theory="storm-failure">The storm damaged the radios and created false echoes.</button>
      <button type="button" data-theory="staged-witness">Silas staged the scene to hide an ordinary crime.</button>
      <button type="button" data-theory="mimic-timeline">Something is imitating officers and transmitting before events occur.</button>
      <button type="button" data-theory="duplicate-units">Two real patrol units were assigned to the same call.</button>
    </div>
    <div id="theoryFeedback" class="info-card" style="margin-top:10px">No theory submitted. Compare clues, then record the explanation that fits the timeline.</div>
    <div class="page-buttons"><button id="submitTheory">Submit case theory</button></div>
    <h3 class="section-title" style="font-size:17px;margin-top:24px">Disappearance log</h3>
    <div id="missingLog" class="info-card">Nothing has gone missing yet. Keep track of the scene.</div>
    <div class="page-buttons"><button id="closeObjectives">Close case file</button></div>
  </div>
</div>
<div id="interviewPanel" class="overlay hidden">
  <div class="witness-frame">
    <section class="witness-camera">
      <div class="witness-camera-label">LIVE CLOSE-UP / ROOM 02<br>DO NOT LOOK AT THE GLASS</div>
      <div id="silasCloseFace" class="silas-close-face"><div class="silas-neck"></div><i class="silas-eye left"></i><i class="silas-eye right"></i><i class="silas-mouth"></i></div>
      <div id="silasZoomCaption" class="witness-caption">Silas is listening to something in the wall behind you.</div>
    </section>
    <section class="witness-dialogue">
      <div class="kicker">Recorded statement · Cypress Farmhouse</div>
      <h2 class="section-title">ONE-ON-ONE / SILAS VENN</h2>
      <p class="intro">The camera keeps pushing closer even though the chair has not moved. Ask carefully. Every answer changes the reliability of the statement.</p>
      <div id="interviewQuestion" class="interview-question"></div>
      <div id="interviewChoices" class="interview-choices"></div>
      <div id="interviewFeedback" class="interview-feedback">Record his answers carefully. Contradictions can be useful.</div>
      <div class="page-buttons"><button id="interviewContinue" class="hidden">Continue interview</button><button id="endInterview" class="hidden">Save statement</button><button id="leaveInterview">End interview</button></div>
    </section>
  </div>
</div>
<div id="stationIntakePanel" class="overlay hidden" aria-label="County police station intake">
  <div class="panel station-panel">
    <div class="kicker">County police station · visitor verification</div>
    <h2 class="section-title">Night Intake / Identity Control</h2>
    <p class="intro">Six visitors arrived after the station's external cameras went dark. Examine every credential, question each visitor, cross-check the roster, then decide whether to admit or detain them. A wrong decision changes what follows you outside.</p>
    <div class="station-topline"><span><span class="station-lamp"></span>CAMERA NETWORK 04 / AUDIO LIVE</span><span id="stationProgress" class="station-score">VISITOR 1 / 6</span><span id="stationThreat" class="station-alert">THREAT: CONTAINED</span></div>
    <div id="stationIncidentBanner" class="station-incident hidden" role="status"></div>
    <div id="stationSummary" class="station-summary hidden"></div>
    <div id="stationCaseView" class="station-layout">
      <section class="station-card">
        <div class="station-feed"><span id="stationFeedTitle">INTAKE WINDOW B</span><span id="stationFeedStatus">REC ●</span></div>
        <div id="stationPortrait" class="station-portrait"><div class="station-face"></div></div>
        <h3 id="stationSuspectName" class="station-name">VISITOR</h3>
        <div id="stationSuspectRole" class="station-role">ID CHECK REQUIRED</div>
        <button id="stationZoomInterview" type="button" class="station-zoom-button">ONE-ON-ONE / CAMERA CLOSE-UP</button>
        <div id="stationIdCard" class="station-doc"><strong>DOCUMENT SCAN</strong>
ID number: UNKNOWN
Photo match: UNCONFIRMED
Authorization: NOT CHECKED</div>
        <div id="stationRegistryCard" class="station-doc" style="margin-top:8px"><strong>ROSTER RESPONSE</strong>
Awaiting database query.</div>
        <div id="stationSuspectStatus" class="station-status">No decision recorded. Ask all three questions before admitting or detaining a visitor.</div>
      </section>
      <section class="station-card">
        <div class="station-feed"><span>INTERVIEW CHANNEL / GLASS 1-WAY</span><span>DO NOT TURN AROUND</span></div>
        <div id="stationChatLog" class="station-chatlog" aria-live="polite"></div>
        <form id="stationComposer" class="station-compose" autocomplete="off">
          <input id="stationChatInput" maxlength="180" placeholder="Ask the visitor a question…" aria-label="Chat with the suspect" autocomplete="off" spellcheck="false">
          <button type="submit">SEND</button>
        </form>
        <div class="station-questions">
          <button type="button" data-station-ask="identity">INSPECT ID / PHOTO</button>
          <button type="button" data-station-ask="purpose">ASK PURPOSE / ALIBI</button>
          <button type="button" data-station-ask="records">CROSS-CHECK ROSTER</button>
        </div>
        <div class="station-topic-questions">
          <button type="button" data-station-topic="camera">ASK ABOUT CAMERA 04</button>
          <button type="button" data-station-topic="extra">ASK ABOUT THE EXTRA ARRIVAL</button>
          <button type="button" data-station-topic="silas">ASK ABOUT SILAS / THE HOUSE</button>
          <button type="button" data-station-topic="door">ASK HOW THEY ENTERED</button>
        </div>
        <div id="stationFeedback" class="station-feedback">The cameras show the visitor entering, but none show the door opening.</div>
        <div id="stationDecisionButtons" class="station-decisions">
          <button type="button" data-station-decision="admit">ADMIT VISITOR</button>
          <button type="button" data-station-decision="detain">DETAIN FOR REVIEW</button>
        </div>
        <div class="page-buttons"><button type="button" id="stationNextVisitor" class="hidden">Record decision · Next visitor</button><button type="button" id="stationReviewFiles" class="hidden">Review flagged files</button><button type="button" id="stationClose">Leave intake desk</button></div>
      </section>
    </div>
  </div>
</div>
<div id="suspectZoomPanel" class="overlay hidden" role="dialog" aria-modal="true" aria-labelledby="suspectZoomName">
  <div class="suspect-zoom-shell">
    <section class="suspect-camera">
      <div class="suspect-camera-label">CAM 04 AUTO-ZOOM / FRAME HOLD<br>DO NOT TRUST THE FEED</div>
      <div id="suspectZoomFigure" class="suspect-zoom-figure"><div class="zoom-body"></div><div class="zoom-head"></div><div class="zoom-hair"></div><div class="zoom-eyes"></div><div class="zoom-mouth"></div></div>
      <div id="suspectZoomCameraStatus" class="suspect-camera-status">AUDIO OPEN · VIDEO TIMESTAMP UNSTABLE</div>
    </section>
    <section class="suspect-dialogue">
      <div class="kicker">Private interview · County Police Station</div>
      <h2 id="suspectZoomName" class="section-title">ONE-ON-ONE INTERVIEW</h2>
      <div id="suspectZoomRole" class="intro">The visitor waits for your question.</div>
      <div id="suspectZoomLine" class="interview-question">Look at the visitor, not the reflection behind them.</div>
      <div class="kicker">CHOOSE YOUR NEXT QUESTION</div>
      <div id="suspectZoomChoices" class="suspect-zoom-choices">
        <button type="button" data-suspect-choice="identity">Why does your photograph look different?</button>
        <button type="button" data-suspect-choice="purpose">Where were you at 02:17?</button>
        <button type="button" data-suspect-choice="records">I'll read the roster to you.</button>
        <button type="button" data-suspect-choice="camera">What did Camera 04 record?</button>
        <button type="button" data-suspect-choice="extra">Who was the extra arrival?</button>
        <button type="button" data-suspect-choice="silas">What do you know about Silas?</button>
      </div>
      <div id="suspectZoomResponse" class="suspect-zoom-response" aria-live="polite">The microphone is live. Their first answer will be added to the station record.</div>
      <div class="page-buttons"><button id="closeSuspectZoom" type="button">RETURN TO INTAKE DESK</button></div>
    </section>
  </div>
</div>
<div id="inventoryPanel" class="overlay hidden">
  <div class="panel">
    <div class="kicker">Field kit</div>
    <h2 class="section-title">Inventory</h2>
    <div id="inventorySummary" class="info-card"></div>
    <div class="inventory-grid">
      <div class="inventory-slot"><span>▣</span>Ammo boxes<br><b id="invAmmo">24</b></div>
      <div class="inventory-slot"><span>✚</span>Medical packs<br><b id="invMed">0</b></div>
      <div class="inventory-slot"><span>ϟ</span>Battery cells<br><b id="invBat">0</b></div>
      <div class="inventory-slot"><span>⌑</span>Relay key<br><b id="invKeys">Missing</b></div>
    </div>
    <div class="page-buttons"><button id="useMed">Use medical pack</button><button id="closeInventory">Close inventory</button></div>
  </div>
</div>
<div id="pausePanel" class="overlay hidden">
  <div class="panel">
    <div class="kicker">Patrol interrupted</div>
    <h2 class="section-title">Paused</h2>
    <p class="intro">The swamp is still there when you return.</p>
    <div class="page-buttons"><button id="resume">Resume patrol</button><button id="pauseObjectives">Case file</button><button id="pauseAccount">Account / Cloud Save</button><button id="pauseMenu">Abandon patrol</button></div>
  </div>
</div>

<div id="huntBanner" aria-live="assertive">THE SMILER HAS YOUR ROUTE<small id="huntBannerSub">RUN · HIDE · KEEP QUIET</small></div>
<div id="realityPulse" aria-hidden="true"></div>
<div id="radioBreachPanel" class="overlay hidden" role="dialog" aria-modal="true" aria-labelledby="radioBreachTitle">
  <div class="radio-breach-shell">
    <div class="radio-breach-top"><span class="radio-breach-signal"><i class="radio-breach-dot"></i> SECURE CHANNEL BREACH</span><span id="radioBreachCount">TRANSMISSION 01 / 02</span></div>
    <h2 id="radioBreachTitle" class="radio-breach-title">YOUR PARTNER IS CALLING FROM INSIDE THE HOUSE</h2>
    <div id="radioBreachCopy" class="radio-breach-copy">The channel opens without a keypress. The voice is almost right.</div>
    <div id="radioBreachTranscript" class="radio-breach-transcript">PARTNER: “I need you to come to the marker. I'm hurt.”
DISPATCH: “No second officer is assigned.”
PARTNER: “Why did you let me in?”</div>
    <div id="radioBreachTimer" class="radio-breach-foot">AUTOMATIC RESPONSE IN 11 SECONDS · ANSWER WHILE YOU MOVE</div>
    <div class="radio-breach-choices">
      <button type="button" data-radio-breach-choice="verify">VERIFY THE CALL SIGN<br><small>Use the case evidence. Risk delay, but do not trust the voice.</small></button>
      <button type="button" data-radio-breach-choice="follow">FOLLOW THE COORDINATES<br><small>Gain a possible lead. The signal may be bait.</small></button>
      <button type="button" data-radio-breach-choice="silence">CUT THE CHANNEL<br><small>Lower your noise. Lose radio help briefly.</small></button>
    </div>
    <div class="radio-breach-foot">DO NOT REPLY WITH YOUR REAL NAME OR PERSONAL INFORMATION.</div>
  </div>
</div>

<div id="endingPanel" class="overlay hidden">
  <div class="panel">
    <div class="kicker">Incident report finalized</div>
    <h2 id="endingTitle" class="section-title">Case closed</h2>
    <p id="endingText" class="intro"></p>
    <div id="endingStats" class="info-card"></div>
    <div class="page-buttons"><button id="again">Start another patrol</button><button id="toMenu">Main menu</button></div>
  </div>
</div>
<div id="radioPanel" class="overlay hidden">
  <div class="panel">
    <div class="kicker">Encrypted dispatch channel</div>
    <h2 class="section-title">Radio transcript</h2>
    <div id="radioText" class="info-card"></div>
    <div class="page-buttons"><button id="closeRadio">Return to patrol</button></div>
  </div>
</div>
<script>
(()=>{
"use strict";
const $=id=>document.getElementById(id);
const canvas=$('game');
const ctx=canvas.getContext('2d',{alpha:false});
const lightCanvas=document.createElement('canvas');
const lightCtx=lightCanvas.getContext('2d');
const mini=$('minimap');
const mctx=mini.getContext('2d');
const WORLD={w:3200,h:2500};
const TILE=32;
const specs={
  hugo:{name:'Officer Hugo',color:'#29372d',shirt:'#777650',speed:158,hp:110,stamina:105,ammo:6,reserve:24,gender:'male',hair:'#29231c'},
  yumi:{name:'Officer Yumi',color:'#303d36',shirt:'#817552',speed:174,hp:95,stamina:125,ammo:6,reserve:26,gender:'female',hair:'#201a18'}
};
const state={
  screen:'menu',
  selectedCharacter:'hugo',
  pendingCharacter:'hugo',
  controlMode:'desktop',
  pendingMode:'desktop',
  options:{shake:true,subtitles:true,personalScares:true,voiceWhispers:true},
  voiceCaptionTimer:0,
  voiceCooldown:0,
  voiceAmbientTimer:16,
  voiceEventFlags:{},
  personalScareTimer:0,
  personalScareCooldown:0,
  personalScareCount:0,
  threatTier:0,
  flashlightFlickerTimer:0,
  running:false,
  paused:false,
  prologueStage:'call',
  prologueTimer:0,
  driveProgress:0,
  driveSpeed:0,
  driveLane:0,
  driveScroll:0,
  driveShake:0,
  driveSirenPhase:0,
  driveNearMissTimer:0,
  drivePassedCars:0,
  driveCollisionCooldown:0,
  driveCrashTimer:0,
  driveDamage:0,
  driveCollisionCount:0,
  driveWheel:0,
  driveGear:1,
  driveRpm:900,
  driveWiper:0,
  driveSkid:0,
  driveHydroplane:0,
  partnerSent:{},
  partnerChatCount:0,
  lastBuildingExit:null,
  sceneFade:0,
  horrorBeat:0,
  gameOver:false,
  won:false,
  floor:'outside',
  room:null,
  elapsed:0,
  missionClock:137,
  lastFrame:0,
  toastTimer:0,
  radioTimer:0,
  lightning:0,
  lightningNext:10,
  screenShake:0,
  damageFlash:0,
  noise:0,
  intensity:0,
  exitHintCooldown:0,
  apparitionTimer:0,
  apparitionCooldown:11,
  apparitionX:0,
  apparitionY:0,
  horrorEventFlags:{},
  storyScareQueue:[],
  indoorPresence:{timer:0,cooldown:7,x:0,y:0,phase:0,arming:0,appearances:0},
  deathFade:0,
  victoryFade:0,
  discovered:0,
  rescued:0,
  keysFound:false,
  witnessInterviewed:false,
  witnessTrust:0,
  stationStage:'idle',
  stationQueue:[],
  stationQueuePosition:0,
  stationRetryMode:false,
  stationDecisions:{},
  stationChecks:{},
  stationChats:{},
  stationTopics:{},
  stationManifestEvents:{},
  stationFeedback:'',
  stationComplete:false,
  stationThreat:0,
  stationCorrect:0,
  stationProcessed:0,
  stationIncidentLogged:false,
  stationAuditTrail:[],
  extractionStarted:false,
  extractionHold:0,
  extractionWave1:false,
  extractionWave2:false,
  extractionWave3:false,
  extractionWave4:false,
  extractionLastToast:0,
  extractionWasOutside:false,
  exploredRoomIds:[],
  caseComparisons:[],
  pendingTheory:'',
  caseTheory:'',
  theoryAttempts:0,
  interviewStep:0,
  interviewAwaitingContinue:false,
  interviewChoiceFeedback:'',
  missingTimer:36,
  missingCount:0,
  missingIds:[],
  roomItemStates:{},
  disappearanceLog:[],
  exploredRooms:0,
  kills:0,
  shots:0,
  saves:0,
  currentWeapon:'service pistol',
  audioReady:false,
  mute:false,
  hideSpotActive:false,
  hideSpotName:'',
  hideRestoreFlashlight:false,
  crawlerSearchToastAt:0,
  hideElapsed:0,
  hideRisk:0,
  screamCooldown:0,
  screamPulseTimer:0,
  screamPulseRadius:0,
  helpCooldown:0,
  helpTimer:0,
  helpCount:0,
  anchorsDestroyed:[],
  anchorsDisabled:false,
  trueEnding:false,
  soundVoidTimer:0,
  soundVoidCooldown:36,
  soundVoidTotal:0,
  finalManifestStarted:false,
  adaptiveHorror:{sprintExposure:0,flashlightExposure:0,hideCount:0,radioChoices:0,verifiedCalls:0,shotsAttracted:0},
  huntActive:false,
  huntTimer:0,
  huntWarning:0,
  huntsTriggered:0,
  huntsSurvived:0,
  nextHuntAt:43,
  huntKind:'',
  radioIncidentCount:0,
  radioIncidentActive:false,
  radioIncidentTimer:0,
  radioSilenceUntil:0,
  nextRadioIncidentAt:42,
  falseSignal:{active:false,x:0,y:0,timer:0,triggered:false},
  trailPhantom:{active:false,x:0,y:0,timer:0,cooldown:15,total:0,phase:0,kind:'edge'},
  realityPulseTimer:0,
  realityPulseCooldown:0,
  realityPulseCount:0,
  lastRealityRoom:'',
  memorialTributeViewed:false
};
let W=innerWidth;
let H=innerHeight;
let dpr=1;
let player=null;
let monster=null;
let crawlers=[];
let survivors=[];
let objects=[];
let bullets=[];
let particles=[];
let trees=[];
let treeGrid=new Map();
let roadDetails=[];
let groundCanvas=null;
let interiorBaseCache={room:null,canvas:null};
let indoorEchoHistory=[];
let indoorEcho={active:false,timer:0,cooldown:13,x:0,y:0,angle:0,phase:0,roomId:'',roomAge:0};
let indoorEchoSampleTimer=0;
let indoorEchoRoomId='';
let outdoorEchoTrail=[];
let outdoorEchoSampleTimer=0;
let outdoorMemoryEcho={active:false,timer:0,cooldown:32,x:0,y:0,angle:0,phase:0,focused:0,seen:false};
let lastMiniDraw=-999;
let lastMiniFloor=null;
let lastMiniRoom=null;
let wetPatches=[];
let reeds=[];
let raindrops=[];
let fireflies=[];
let decals=[];
let interiorProps=[];
let camera={x:0,y:0};
let keys={};
let pointer={x:W/2,y:H/2,down:false};
let touchRun=false;
let ammo=6;
let reserve=24;
let evidence=0;
let caseRecords=[];
let medkits=0;
let batteryCells=1;
let flashlightBattery=100;
let flashlight=true;
let stamina=100;
let health=100;
let footstepTimer=0;
let attackTimer=0;
let shootTimer=0;
let reloadTimer=0;
let interactCooldown=0;
let damageCooldown=0;
let growlTimer=4;
let ambientTimer=0;
let shakeX=0;
let shakeY=0;
let audioContext=null;
let masterGain=null;
let ambientOsc=null;
let ambientBedGain=null;
let rainGain=null;
let rainSource=null;
let uiStack=[];
let objectivePageOpen=false;
let inventoryPageOpen=false;
let lastSafe={x:260,y:260};
function clamp(v,min,max){return Math.max(min,Math.min(max,v))}
function lerp(a,b,t){return a+(b-a)*t}
function dist(ax,ay,bx,by){return Math.hypot(bx-ax,by-ay)}
function angleTo(ax,ay,bx,by){return Math.atan2(by-ay,bx-ax)}
function seeded(x,y){let n=Math.sin(x*127.1+y*311.7+17.17)*43758.5453;return n-Math.floor(n)}
function choose(list){return list[Math.floor(Math.random()*list.length)]}
function resize(){
  dpr=Math.min(window.devicePixelRatio||1,window.innerWidth<900?1.2:1.5);
  W=innerWidth;
  H=innerHeight;
  canvas.width=Math.floor(W*dpr);
  canvas.height=Math.floor(H*dpr);
  lightCanvas.width=canvas.width;
  lightCanvas.height=canvas.height;
  canvas.style.width=W+'px';
  canvas.style.height=H+'px';
  ctx.setTransform(dpr,0,0,dpr,0,0);
  lightCtx.setTransform(dpr,0,0,dpr,0,0);
}
window.addEventListener('resize',resize);
resize();
function setScreen(name){
  state.screen=name;
  const mapping={
    menu:'menu',
    character:'characterPanel',
    controls:'controlsPanel',
    how:'howPanel',
    credits:'creditsPanel',
    objectives:'objectivePanel',
    memorial:'memorialPanel',
    inventory:'inventoryPanel',
    pause:'pausePanel',
    ending:'endingPanel',
    radio:'radioPanel',
    account:'accountPanel',
    interview:'interviewPanel',
    stationIntake:'stationIntakePanel'
  };
  for(const id of Object.values(mapping))$(id).classList.add('hidden');
  const suspectZoom=$('suspectZoomPanel');if(suspectZoom)suspectZoom.classList.add('hidden');
  if(mapping[name])$(mapping[name]).classList.remove('hidden');
  if(name==='menu'||name==='character'||name==='controls'||name==='how'||name==='credits'){
    state.running=false;
    document.body.classList.remove('game-active');
  }
  if(name==='menu')drawMenuArt();
  if(name!=='game'){
    document.body.classList.remove('prologue-mode','prologue-call','prologue-drive','prologue-arrival');
  }
}
function triggerPersonalScare(kind){
  if(!state.options.personalScares||state.personalScareCount>=3||state.personalScareCooldown>0||state.personalScareTimer>0)return;
  const officer=specs[state.selectedCharacter].name.toUpperCase();
  const records={
    personnel:{title:'YOU WERE NEVER ALONE',message:'OFFICER: '+officer+'\nPERSONNEL FILE OPENED FROM INSIDE THE EMPTY HOUSE.\nTHE BODYCAM SHOWS YOU STANDING PERFECTLY STILL.\nTHEN WHO IS MOVING BEHIND YOU?',stamp:'BODYCAM 04:17:09 // FRAME DOES NOT MATCH'},
    contact:{title:'SOMEONE ANSWERED YOUR RADIO',message:'EMERGENCY CONTACT: UNKNOWN\nCALL ORIGIN: INSIDE THE WALLS\nNO SECOND OFFICER WAS DISPATCHED.\nDO NOT LOOK BEHIND YOU.',stamp:'RADIO CHANNEL 0 // VOICEPRINT MATCH: YOURS'},
    duplicate:{title:'SECOND OFFICER DETECTED',message:'SUBJECT: '+officer+'\nACTIVE RECORDS: 2\nONE RECORD IS STANDING BEHIND YOU.\nTHE OTHER ONE IS READING THIS MESSAGE.',stamp:'IDENTITY CONFLICT // BOTH SUBJECTS ACTIVE'},
    address:{title:'THE FILE KNOWS WHERE YOU ARE',message:'LOCATION: MILE MARKER 9\nENTRY SOURCE: UNKNOWN\nREAL-WORLD PERSONAL DATA: NOT ACCESSED.\nTHIS FICTIONAL RECORD WAS CREATED JUST NOW.',stamp:'LOCAL CASE FILE // NO PRIVATE DATA ACCESSED'}
  };
  const record=records[kind]||records.personnel;
  const overlay=$('personalScare');
  overlay.classList.remove('variant-personnel','variant-contact','variant-duplicate','variant-address','active');
  void overlay.offsetWidth;
  overlay.classList.add('variant-'+(records[kind]?kind:'personnel'),'active');
  $('scareTitle').textContent=record.title;
  $('scareMessage').textContent=record.message;
  $('scareStamp').textContent=record.stamp;
  overlay.setAttribute('aria-hidden','false');
  state.personalScareTimer=2.05;
  state.personalScareCooldown=7.2;
  state.personalScareCount++;
  state.screenShake=Math.max(state.screenShake,.78);
  state.driveShake=Math.max(state.driveShake,.88);
  state.intensity=Math.max(state.intensity,.86);
  sound('scare');
  tone(1180,.055,'square',.20,-980);
  tone(43,.86,'sawtooth',.24,-19);
  tone(170,.42,'triangle',.16,510);
  tone(31,1.05,'sawtooth',.17,-7);
  voiceNoise(choose(['left','right']),.27);
  if(state.options.voiceWhispers){
    const lines={personnel:'Look at the doorway.',contact:'I am inside the wall.',duplicate:'I am the other officer.',address:'You brought it inside.'};
    speakWhisper(lines[kind]||lines.personnel,choose(['left','right']));
  }
}
function queueStoryScare(kind,key,delay=0.8){
  if(!state.options.personalScares||state.personalScareCount>=3||state.horrorEventFlags[key])return;
  state.horrorEventFlags[key]=true;
  if(!Array.isArray(state.storyScareQueue))state.storyScareQueue=[];
  state.storyScareQueue.push({kind,delay:Math.max(0,delay)});
}
function updatePersonalScare(dt){
  state.personalScareCooldown=Math.max(0,state.personalScareCooldown-dt);
  if(state.personalScareTimer>0){
    state.personalScareTimer=Math.max(0,state.personalScareTimer-dt);
    if(state.personalScareTimer===0){const overlay=$('personalScare');overlay.classList.remove('active','variant-personnel','variant-contact','variant-duplicate','variant-address');overlay.setAttribute('aria-hidden','true');}
  }
}
function voiceNoise(side='center',strength=.12){
  if(!audioContext||!masterGain||state.mute)return;
  try{
    const length=Math.floor(audioContext.sampleRate*.68);
    const buffer=audioContext.createBuffer(1,length,audioContext.sampleRate);
    const values=buffer.getChannelData(0);
    for(let i=0;i<length;i++)values[i]=(Math.random()*2-1)*(.65+Math.random()*.35);
    const source=audioContext.createBufferSource();
    source.buffer=buffer;
    const high=audioContext.createBiquadFilter();
    high.type='highpass';high.frequency.value=390;
    const low=audioContext.createBiquadFilter();
    low.type='lowpass';low.frequency.value=1650;
    const gain=audioContext.createGain();
    const pan=audioContext.createStereoPanner?audioContext.createStereoPanner():null;
    const now=audioContext.currentTime;
    gain.gain.setValueAtTime(.001,now);
    gain.gain.linearRampToValueAtTime(strength,now+.08);
    gain.gain.setValueAtTime(strength*.72,now+.26);
    gain.gain.exponentialRampToValueAtTime(.001,now+.66);
    source.connect(high);high.connect(low);low.connect(gain);
    if(pan){pan.pan.value=side==='left'?-0.82:side==='right'?.82:0;gain.connect(pan);pan.connect(masterGain)}else gain.connect(masterGain);
    source.start(now);source.stop(now+.7);
    tone(side==='left'?94:side==='right'?87:91,.42,'triangle',.045,-28);
  }catch(error){}
}
function speakWhisper(line,side='center'){
  if(!state.options.voiceWhispers)return;
  voiceNoise(side,.065);
  try{
    if(!('speechSynthesis' in window)||!window.SpeechSynthesisUtterance)return;
    window.speechSynthesis.cancel();
    const utterance=new SpeechSynthesisUtterance(line);
    utterance.lang='en-US';
    utterance.rate=.70+Math.random()*.12;
    utterance.pitch=.28+Math.random()*.16;
    utterance.volume=.56;
    const voices=window.speechSynthesis.getVoices();
    const candidates=voices.filter(v=>/^en(-|_)/i.test(v.lang));
    if(candidates.length)utterance.voice=candidates[Math.floor(Math.random()*candidates.length)];
    window.speechSynthesis.speak(utterance);
  }catch(error){}
}
function triggerWhisper(line,side='center',who='VOICE UNDER THE STATIC'){
  if(!state.options.voiceWhispers||state.voiceCooldown>0)return false;
  const subtitle=$('voiceSubtitle');
  const words=$('voiceWords');
  const sender=$('voiceWho');
  if(subtitle&&words&&sender){
    words.textContent='“'+line+'”';
    sender.textContent=who+(side==='left'?' · LEFT CHANNEL':side==='right'?' · RIGHT CHANNEL':' · CLOSE TO THE MIC');
    subtitle.className='active '+side;
    state.voiceCaptionTimer=Math.max(3.1,Math.min(5.5,line.length*.055));
  }
  state.voiceCooldown=4.7;
  state.intensity=Math.max(state.intensity,.22);
  state.screenShake=Math.max(state.screenShake,.08);
  speakWhisper(line,side);
  return true;
}
function oneShotWhisper(key,line,side='center',who='VOICE UNDER THE STATIC'){
  if(state.voiceEventFlags[key])return;
  if(triggerWhisper(line,side,who))state.voiceEventFlags[key]=true;
}
function updateWhispers(dt){
  state.voiceCooldown=Math.max(0,state.voiceCooldown-dt);
  if(state.voiceCaptionTimer>0){
    state.voiceCaptionTimer=Math.max(0,state.voiceCaptionTimer-dt);
    if(state.voiceCaptionTimer===0){const subtitle=$('voiceSubtitle');if(subtitle)subtitle.className='';}
  }
  if(!state.options.voiceWhispers||!state.running||state.paused||state.gameOver)return;
  if(state.prologueStage==='drive'){
    if(state.driveProgress>10)oneShotWhisper('drive10','Don’t look behind you.', 'right','UNIDENTIFIED VOICE');
    if(state.driveProgress>31)oneShotWhisper('drive31','Your partner is not outside with you.', 'left','VOICE ON A DEAD CHANNEL');
    if(state.driveProgress>58)oneShotWhisper('drive58','You have already passed this road.', 'center','VOICE UNDER THE ENGINE');
    if(state.driveProgress>82)oneShotWhisper('drive82','When you arrive, keep the flashlight on. It hates the light.', 'right','UNIDENTIFIED VOICE');
    if(state.prologueTimer>12&&!state.voiceEventFlags.driveRadio){
      oneShotWhisper('driveRadio','Unit fourteen is already there. It is standing beside the empty road.', 'left','DISPATCH // IMPOSSIBLE TRANSMISSION');
    }
  }else if(state.prologueStage==='arrival'){
    if(state.prologueTimer>1.6)oneShotWhisper('arrival16','Do not open the door. That is not your partner outside.', 'right','VOICE FROM THE REAR SEAT');
    if(state.prologueTimer>5.5)oneShotWhisper('arrival55','It knows which one you are.', 'center','VOICE IN THE RADIO SPEAKER');
  }else if(state.prologueStage==='swamp'){
    if(state.elapsed>2.8)oneShotWhisper('swamp28','Keep the light moving. It can hear you thinking.', 'left','WHISPER FROM THE TREES');
    if(state.elapsed>9)oneShotWhisper('swamp9','Officer '+specs[state.selectedCharacter].name.replace('Officer ','')+'… please turn around.', 'right','VOICE JUST BEHIND YOU');
    if(state.elapsed>20)oneShotWhisper('swamp20','I can see the little light shaking in your hand.', 'center','UNKNOWN CHANNEL');
    if(evidence>=1)oneShotWhisper('firstEvidence','You found it. Now put it back before it notices.', 'left','VOICE IN THE RECORDER');
    if(state.floor==='inside')oneShotWhisper('insideVoice','There is one more person in this room than you can see.', 'right','VOICE FROM INSIDE THE WALL');
    if(monster&&monster.active&&!monster.hidden&&dist(player.x,player.y,monster.x,monster.y)<360)oneShotWhisper('nearMonster','Don’t point that light at me. I’m the one who called you.', 'center','THE SMILER');
    state.voiceAmbientTimer-=dt;
    if(state.elapsed>24&&state.voiceAmbientTimer<=0){
      const lines=[
        ['Your radio is breathing. Can you hear it?','left','LOW WHISPER'],
        ['Don’t answer if you hear your own voice.','right','VOICE BEHIND THE TREES'],
        ['The hallway is still lit. Something is standing inside the wall.','center','DISTANT RADIO'],
        ['You left somebody behind.','left','CHILDLIKE WHISPER'],
        ['I saw you before you were born.','right','BROKEN TRANSMISSION'],
        ['This is not the way out. You know that.','center','VOICE IN THE FOG'],
        ['Officer… your partner has been dead for three days.','left','DISPATCH // CORRUPTED'],
        ['Stop walking. Listen to the footsteps behind yours.','right','VOICE CLOSE TO YOUR EAR']
      ];
      const picked=choose(lines);
      if(triggerWhisper(picked[0],picked[1],picked[2]))state.voiceAmbientTimer=19+Math.random()*17;
      else state.voiceAmbientTimer=1.1;
    }
  }
}
function toast(message,duration=2.5){
  $('toast').textContent=message;
  $('toast').style.display='block';
  state.toastTimer=duration;
}
function hideToast(){
  $('toast').style.display='none';
  state.toastTimer=0;
}
function audioStart(){
  if(state.audioReady)return;
  try{
    const AC=window.AudioContext||window.webkitAudioContext;
    if(!AC)return;
    audioContext=new AC();
    masterGain=audioContext.createGain();
    masterGain.gain.value=.18;
    masterGain.connect(audioContext.destination);
    ambientOsc=audioContext.createOscillator();
    const lowFilter=audioContext.createBiquadFilter();
    ambientBedGain=audioContext.createGain();
    ambientOsc.type='sawtooth';
    ambientOsc.frequency.value=38;
    lowFilter.type='lowpass';
    lowFilter.frequency.value=115;
    ambientBedGain.gain.value=.09;
    ambientOsc.connect(lowFilter);
    lowFilter.connect(ambientBedGain);
    ambientBedGain.connect(masterGain);
    ambientOsc.start();
    rainGain=audioContext.createGain();
    rainGain.gain.value=.018;
    const buffer=audioContext.createBuffer(1,audioContext.sampleRate*2,audioContext.sampleRate);
    const data=buffer.getChannelData(0);
    for(let i=0;i<data.length;i++)data[i]=(Math.random()*2-1)*.25;
    rainSource=audioContext.createBufferSource();
    rainSource.buffer=buffer;
    rainSource.loop=true;
    const rainFilter=audioContext.createBiquadFilter();
    rainFilter.type='lowpass';
    rainFilter.frequency.value=950;
    rainSource.connect(rainFilter);
    rainFilter.connect(rainGain);
    rainGain.connect(masterGain);
    rainSource.start();
    state.audioReady=true;
  }catch(error){state.audioReady=false}
}
function setAmbientBed(enabled){
  if(!audioContext)return;
  const now=audioContext.currentTime;
  try{
    if(ambientBedGain)ambientBedGain.gain.setTargetAtTime(enabled?.09:.0001,now,.09);
    if(rainGain)rainGain.gain.setTargetAtTime(enabled?.018:.0001,now,.07);
  }catch(error){}
}
function tone(freq,duration,type='sine',volume=.12,slide=0){
  if(!audioContext||!masterGain||state.mute)return;
  try{
    const now=audioContext.currentTime;
    const osc=audioContext.createOscillator();
    const gain=audioContext.createGain();
    osc.type=type;
    osc.frequency.setValueAtTime(Math.max(25,freq),now);
    osc.frequency.exponentialRampToValueAtTime(Math.max(25,freq+slide),now+duration);
    gain.gain.setValueAtTime(volume,now);
    gain.gain.exponentialRampToValueAtTime(.001,now+duration);
    osc.connect(gain);
    gain.connect(masterGain);
    osc.start(now);
    osc.stop(now+duration+.03);
  }catch(error){}
}
function sound(name){
  if(name==='shot'){
    tone(115,.12,'sawtooth',.42,-75);
    tone(45,.19,'triangle',.25,-20);
  }
  if(name==='reload'){
    tone(480,.04,'square',.08,-180);
    setTimeout(()=>tone(310,.06,'square',.08,-90),150);
    setTimeout(()=>tone(540,.05,'square',.07,-260),370);
  }
  if(name==='pickup'){
    tone(620,.09,'sine',.12,130);
    setTimeout(()=>tone(880,.12,'sine',.1,80),75);
  }
  if(name==='hurt'){
    tone(80,.24,'sawtooth',.26,-45);
    tone(53,.3,'triangle',.16,-15);
  }
  if(name==='radio'){
    tone(750,.035,'square',.04,-340);
    setTimeout(()=>tone(510,.045,'square',.035,-400),65);
  }
  if(name==='scare'){
    tone(50,.8,'sawtooth',.28,-25);
    tone(110,.6,'square',.12,-70);
  }
  if(name==='step'){
    tone(65,.045,'triangle',.025,-22);
  }
  if(name==='door'){
    tone(95,.2,'triangle',.12,-35);
    setTimeout(()=>tone(210,.13,'square',.07,-120),110);
  }
  if(name==='roar'){
    tone(64,.6,'sawtooth',.22,-48);
    tone(39,.8,'triangle',.22,-12);
  }
}
function initializeAssets(){
  trees=[];
  wetPatches=[];
  reeds=[];
  raindrops=[];
  fireflies=[];
  decals=[];
  for(let x=35;x<WORLD.w;x+=63){
    for(let y=35;y<WORLD.h;y+=67){
      const n=seeded(x,y);
      const tx=x+(n*31),ty=y+seeded(y,x)*29;
      const onRoad=nearRoad(tx,ty);
      const nearBuilding=buildingAt(tx,ty,110);
      const onFootpath=nearFootpath(tx,ty,61);
      if(n>.57&&!onRoad&&!nearBuilding&&!onFootpath){
        trees.push({x:tx,y:ty,s:.62+seeded(x+4,y+7)*.92,shade:Math.floor(seeded(x+7,y+3)*3),phase:seeded(y,x)*6.28,solid:true});
      }
      if(n<.09&&!onRoad){
        wetPatches.push({x:x+10,y:y+14,w:18+seeded(x+2,y)*42,h:5+seeded(x,y+8)*10});
      }
      if(n>.86&&!onRoad){
        reeds.push({x:x+12,y:y+8,h:9+seeded(y+1,x)*17,phase:seeded(x+5,y)*6});
      }
    }
  }
  for(let i=0;i<55;i++){
    fireflies.push({x:seeded(i*7,2)*WORLD.w,y:seeded(i*11,4)*WORLD.h,phase:seeded(i,4)*7,speed:.5+seeded(i,9)});
  }
  for(let i=0;i<Math.min(115,Math.max(70,Math.floor(W*H/14000)));i++){
    raindrops.push({x:Math.random()*W,y:Math.random()*H,speed:190+Math.random()*460,length:7+Math.random()*8});
  }
  buildTreeGrid();
  buildRoadDetails();
  if(!groundCanvas)buildGroundCache();
  interiorBaseCache={room:null,canvas:null};
}
function roadPoints(){
  return [
    {x:120,y:-80},
    {x:320,y:280},
    {x:560,y:520},
    {x:850,y:790},
    {x:1150,y:945},
    {x:1520,y:1120},
    {x:1900,y:1390},
    {x:2240,y:1620},
    {x:2580,y:1960},
    {x:3080,y:2440}
  ];
}
function roadNetworks(){
  return [
    roadPoints(),
    [{x:320,y:280},{x:170,y:430},{x:125,y:690},{x:205,y:970},{x:410,y:1130}],
    [{x:560,y:520},{x:370,y:665},{x:360,y:850},{x:505,y:1035},{x:690,y:1130}],
    [{x:850,y:790},{x:1050,y:660},{x:1340,y:650},{x:1570,y:790},{x:1710,y:980}],
    [{x:1150,y:945},{x:1060,y:1180},{x:1110,y:1430},{x:1330,y:1610},{x:1650,y:1720}],
    [{x:1520,y:1120},{x:1740,y:970},{x:2020,y:1000},{x:2270,y:1180},{x:2510,y:1190}],
    [{x:1900,y:1390},{x:2030,y:1600},{x:2260,y:1760},{x:2520,y:1800},{x:2760,y:2020}],
    [{x:410,y:1130},{x:450,y:1500},{x:740,y:1670},{x:980,y:1840},{x:1290,y:1920}],
    [{x:1710,y:980},{x:1850,y:760},{x:2130,y:710},{x:2410,y:780},{x:2630,y:920}],
    [{x:2520,y:1800},{x:2790,y:1740},{x:3050,y:1840}]
  ];
}
const FOOTPATHS=[
  [{x:250,y:300},{x:270,y:275},{x:355,y:270},{x:460,y:328},{x:520,y:405},{x:560,y:520},{x:690,y:605},{x:820,y:690},{x:930,y:735}],
  [{x:520,y:405},{x:480,y:440},{x:420,y:470},{x:375,y:470}],
  [{x:690,y:605},{x:720,y:900}],
  [{x:930,y:735},{x:980,y:530},{x:1040,y:360},{x:1210,y:445},{x:1480,y:470}],
  [{x:930,y:735},{x:1110,y:660}],
  [{x:560,y:520},{x:480,y:700},{x:720,y:900}],
  [{x:850,y:790},{x:1150,y:945},{x:1425,y:970},{x:1540,y:1100},{x:1690,y:1300},{x:1990,y:1450}],
  [{x:1150,y:945},{x:1100,y:1350},{x:980,y:1840},{x:1290,y:1920},{x:1370,y:2110}],
  [{x:1990,y:1450},{x:2240,y:1620},{x:2390,y:1740},{x:2580,y:1960},{x:2920,y:2300}],
  [{x:2240,y:1620},{x:2180,y:1870}],
  [{x:2240,y:1620},{x:2270,y:1180},{x:2510,y:1190},{x:2700,y:1080}],
  [{x:2700,y:1080},{x:2760,y:1350},{x:2820,y:1570},{x:2790,y:1740}],
  [{x:2580,y:1960},{x:2790,y:1740},{x:3050,y:1840}],
  [{x:690,y:605},{x:850,y:790},{x:930,y:735}],
  [{x:1540,y:1100},{x:1710,y:980},{x:1850,y:760},{x:2130,y:710},{x:2410,y:780}]
];
function footpathDistance(x,y){
  let result=Infinity;
  for(const points of FOOTPATHS){
    for(let i=0;i<points.length-1;i++){
      const d=pointSegmentDistance(x,y,points[i],points[i+1]);
      if(d<result)result=d;
    }
  }
  return result;
}
function nearFootpath(x,y,width=58){return footpathDistance(x,y)<width;}
function pointSegmentDistance(px,py,a,b){
  const dx=b.x-a.x;
  const dy=b.y-a.y;
  const l=dx*dx+dy*dy||1;
  const t=clamp(((px-a.x)*dx+(py-a.y)*dy)/l,0,1);
  return dist(px,py,a.x+dx*t,a.y+dy*t);
}
function nearRoad(x,y){
  for(const points of roadNetworks()){
    for(let i=0;i<points.length-1;i++){
      if(pointSegmentDistance(x,y,points[i],points[i+1])<84)return true;
    }
  }
  return false;
}
function roadDistance(x,y){
  let result=Infinity;
  for(const points of roadNetworks()){
    for(let i=0;i<points.length-1;i++)result=Math.min(result,pointSegmentDistance(x,y,points[i],points[i+1]));
  }
  return result;
}
function buildTreeGrid(){
  treeGrid=new Map();
  for(const t of trees){
    const gx=Math.floor(t.x/128),gy=Math.floor(t.y/128),key=gx+','+gy;
    if(!treeGrid.has(key))treeGrid.set(key,[]);
    treeGrid.get(key).push(t);
  }
}
function treeNear(x,y,rx,ry){
  const minX=Math.floor((x-rx)/128),maxX=Math.floor((x+rx)/128);
  const minY=Math.floor((y-ry)/128),maxY=Math.floor((y+ry)/128);
  for(let gx=minX;gx<=maxX;gx++)for(let gy=minY;gy<=maxY;gy++){
    const bucket=treeGrid.get(gx+','+gy);
    if(!bucket)continue;
    for(const t of bucket)if(Math.abs(t.x-x)<=rx&&Math.abs(t.y-y)<=ry&&dist(x,y,t.x,t.y)<18*t.s)return true;
  }
  return false;
}
function buildRoadDetails(){
  roadDetails=[];
  for(let i=0;i<60;i++){
    const x=130+(i*173)%3000;
    const y=75+(i*197)%2350;
    if(roadDistance(x,y)<49)roadDetails.push({x,y,i});
  }
}
function addParticle(p){
  if(particles.length>=260)particles.splice(0,particles.length-220);
  particles.push(p);
}

function buildingAt(x,y,padding=0){
  const list=[
    {x:375,y:390,w:145,h:112},
    {x:930,y:735,w:170,h:132},
    {x:1480,y:470,w:164,h:120},
    {x:1690,y:1300,w:170,h:132},
    {x:2390,y:1740,w:178,h:136}
  ];
  for(const o of objects){
    if(o.type==='building')list.push({x:o.x,y:o.y,w:o.w,h:o.h});
  }
  return list.some(b=>x>b.x-b.w/2-padding&&x<b.x+b.w/2+padding&&y>b.y-b.h/2-padding&&y<b.y+b.h/2+padding);
}
function makeObjects(){
  objects=[
    {id:'log',x:460,y:328,type:'evidence',name:'Waterlogged patrol log',detail:'A page from Unit 14. The time is scratched out.',found:false,icon:'▤'},
    {id:'radio',x:690,y:605,type:'evidence',name:'Cracked dispatch radio',detail:'A second voice can be heard under the static.',found:false,icon:'▣'},
    {id:'cloth',x:1040,y:360,type:'evidence',name:'Torn uniform patch',detail:'The fabric is wet, but there has been no rain indoors.',found:false,icon:'▧'},
    {id:'prints',x:1425,y:970,type:'evidence',name:'Oversized footprints',detail:'The prints lead into the black water. None lead back.',found:false,icon:'⌁'},
    {id:'badge',x:1990,y:1450,type:'evidence',name:'Deputy Harlow’s badge',detail:'The metal is warm. Someone recently held it.',found:false,icon:'★'},
    {id:'shack',x:375,y:390,type:'building',name:'Checkpoint shack',detail:'A roadside patrol hut with a jammed window.',room:'checkpoint',w:145,h:112},
    {id:'station',x:930,y:735,type:'building',name:'County Police Station',detail:'The night intake desk is still processing visitors although the station was evacuated.',room:'station',w:170,h:132},
    {id:'gas',x:1480,y:470,type:'building',name:'Swamp gas stop',detail:'A shut-down gas stop with an office in back.',room:'gas',w:164,h:120},
    {id:'cabin',x:1690,y:1300,type:'building',name:'Leaning cabin',detail:'A cabin with fresh light underneath the door.',room:'cabin',w:170,h:132},
    {id:'tower',x:2390,y:1740,type:'building',name:'Radio relay hut',detail:'The emergency relay is still receiving something.',room:'tower',w:178,h:136,style:'relay'},
    {id:'motel',x:110,y:1100,type:'building',name:'Pine Rest Motel',detail:'A roadside motel with a vacancy sign that keeps switching off.',room:'motel',w:188,h:144,style:'motel'},
    {id:'diner',x:720,y:900,type:'building',name:'Last Stop Diner',detail:'The counter is empty, but one coffee is still steaming.',room:'diner',w:196,h:138,style:'diner'},
    {id:'clinic',x:1210,y:445,type:'building',name:'County Clinic',detail:'The emergency lights are on. Nobody answers the door.',room:'clinic',w:184,h:142,style:'clinic'},
    {id:'depot',x:2700,y:1080,type:'building',name:'Road Maintenance Depot',detail:'A maintenance depot with a broken gate and abandoned tools.',room:'depot',w:196,h:150,style:'depot'},
    {id:'church',x:2180,y:1870,type:'building',name:'St. Mercy Chapel',detail:'Candles glow inside although the power is gone.',room:'church',w:174,h:160,style:'chapel'},
    {id:'warehouse',x:1370,y:2110,type:'building',name:'Flood Control Warehouse',detail:'The warehouse doors are chained from the inside.',room:'warehouse',w:210,h:158,style:'warehouse'},
    {id:'farmhouse',x:2820,y:1570,type:'building',name:'Cypress Farmhouse',detail:'A farmhouse with a light moving behind its upstairs window.',room:'farmhouse',w:182,h:146,style:'farmhouse'},
    {id:'medkit1',x:500,y:430,type:'loot',name:'First-aid pouch',loot:'medkit',found:false,icon:'+'},
    {id:'ammo1',x:1010,y:805,type:'loot',name:'Ammunition box',loot:'ammo',found:false,icon:'▪'},
    {id:'battery1',x:1525,y:520,type:'loot',name:'Flashlight batteries',loot:'battery',found:false,icon:'ϟ'},
    {id:'ammo2',x:2225,y:1590,type:'loot',name:'Emergency ammo pouch',loot:'ammo',found:false,icon:'▪'},
    {id:'exit',x:2920,y:2300,type:'exit',name:'Emergency extraction beacon',detail:'A portable emergency beacon awaits a completed case file and the relay override key.',icon:'✦'}
  ];
  survivors=[
    {id:'ana',x:1110,y:660,name:'Mara',found:false,following:false,delivered:false,hp:1,dialogue:'Please, please get me out of here. It keeps calling from the trees.'},
    {id:'wade',x:1970,y:1450,name:'Eli',found:false,following:false,delivered:false,hp:1,dialogue:'I heard my partner on the radio. He was standing right in front of me when it spoke.'}
  ];
}
function makeRoom(name){
  const rooms={
    checkpoint:{title:'CHECKPOINT SHACK',w:700,h:480,spawn:{x:350,y:392},exit:{x:350,y:435},color:'#453f30',props:[{x:205,y:150,w:110,h:52,t:'desk'},{x:500,y:150,w:80,h:75,t:'cabinet'},{x:440,y:310,w:120,h:40,t:'bed'}],items:[{x:220,y:175,type:'note',name:'Incident memo',detail:'“Do not answer a voice if it uses your badge number.”',found:false},{x:505,y:270,type:'loot',name:'Small ammo stash',loot:'ammo',found:false}]},
    station:{title:'COUNTY POLICE STATION — INTAKE',w:1000,h:700,spawn:{x:500,y:610},exit:{x:500,y:666},color:'#20251f',props:[{x:250,y:185,w:240,h:64,t:'desk'},{x:550,y:180,w:100,h:74,t:'console'},{x:780,y:170,w:88,h:126,t:'cabinet'},{x:180,y:365,w:150,h:46,t:'table'},{x:475,y:390,w:190,h:48,t:'table'},{x:810,y:420,w:110,h:55,t:'shelves'},{x:690,y:560,w:155,h:40,t:'bed'}],items:[{id:'station-intake-terminal',x:250,y:232,type:'intakeDesk',name:'Visitor screening terminal',detail:'Inspect credentials, ask questions, cross-check the roster, and record a decision.',found:false},{id:'station-report',x:550,y:220,type:'note',name:'After-hours intake memo',detail:'“Six visitors are expected. The exterior camera log records seven arrivals. Do not accept a badge merely because it bears the correct seal.”',found:false},{id:'station-medkit',x:780,y:320,type:'loot',name:'Evidence-room medical supplies',loot:'medkit',found:false},{id:'station-tape',x:475,y:420,type:'note',name:'Intercom maintenance tape',detail:'The microphone records the intake clerk whispering when the booth is empty. The file timestamp is tomorrow.',found:false},{id:'station-grandfather-tribute',x:900,y:300,type:'memorial',name:'Framed remembrance — Yumi’s grandfather',detail:'A small, warm-lit frame honours Yumi’s grandfather and his love of planes, cars, and photography.',found:false}]},
    gas:{title:'SWAMP GAS STOP',w:760,h:500,spawn:{x:380,y:412},exit:{x:380,y:458},color:'#3d3b2d',props:[{x:145,y:130,w:100,h:150,t:'shelves'},{x:300,y:130,w:100,h:150,t:'shelves'},{x:560,y:120,w:130,h:70,t:'desk'},{x:520,y:320,w:115,h:45,t:'table'}],items:[{x:560,y:155,type:'note',name:'Receipt with a warning',detail:'“Do not follow the headlights past mile marker 9.”',found:false},{x:320,y:310,type:'loot',name:'Battery pack',loot:'battery',found:false}]},
    cabin:{title:'LEANING CABIN',w:760,h:520,spawn:{x:380,y:432},exit:{x:380,y:478},color:'#41372d',props:[{x:180,y:140,w:120,h:75,t:'bed'},{x:540,y:145,w:100,h:100,t:'cabinet'},{x:350,y:160,w:100,h:50,t:'desk'},{x:530,y:330,w:130,h:46,t:'table'}],items:[{x:350,y:190,type:'note',name:'Handwritten warning',detail:'It stands perfectly still until you use the flashlight.',found:false},{x:550,y:270,type:'loot',name:'Dead flashlight cell',loot:'battery',found:false}]},
    tower:{title:'RADIO RELAY HUT',w:800,h:560,spawn:{x:400,y:472},exit:{x:400,y:520},color:'#30392f',props:[{x:170,y:130,w:110,h:70,t:'desk'},{x:400,y:140,w:200,h:100,t:'console'},{x:650,y:170,w:75,h:120,t:'cabinet'},{x:380,y:340,w:180,h:50,t:'table'}],items:[{x:400,y:190,type:'note',name:'Final dispatch tape',detail:'The voice on the recording says your next line before you speak it.',found:false},{x:650,y:300,type:'loot',name:'Emergency medical pack',loot:'medkit',found:false},{x:250,y:400,type:'loot',name:'Relay override key',loot:'keys',found:false}]}
  };
  rooms.motel=structuredClone(rooms.cabin);
  rooms.motel.title='PINE REST MOTEL';
  rooms.motel.w=920;rooms.motel.h=620;rooms.motel.spawn={x:460,y:520};rooms.motel.exit={x:460,y:574};
  rooms.motel.props=[{x:170,y:145,w:118,h:70,t:'bed'},{x:390,y:140,w:120,h:55,t:'desk'},{x:700,y:155,w:90,h:115,t:'cabinet'},{x:230,y:355,w:150,h:48,t:'table'},{x:650,y:390,w:100,h:55,t:'bed'}];
  rooms.motel.items=[{x:395,y:170,type:'loot',name:'Motel first-aid kit',loot:'medkit',found:false},{x:700,y:300,type:'loot',name:'Motel ammunition tin',loot:'ammo',found:false}];
  rooms.diner=structuredClone(rooms.gas);
  rooms.diner.title='LAST STOP DINER';
  rooms.diner.w=900;rooms.diner.h=600;rooms.diner.spawn={x:450,y:500};rooms.diner.exit={x:450,y:554};
  rooms.diner.props=[{x:185,y:155,w:180,h:42,t:'table'},{x:420,y:155,w:180,h:42,t:'table'},{x:660,y:155,w:140,h:42,t:'table'},{x:180,y:340,w:220,h:46,t:'desk'},{x:685,y:350,w:85,h:130,t:'shelves'}];
  rooms.diner.items=[{x:180,y:370,type:'loot',name:'Diner medical bag',loot:'medkit',found:false},{x:685,y:300,type:'loot',name:'Diner spare batteries',loot:'battery',found:false}];
  rooms.clinic=structuredClone(rooms.station);
  rooms.clinic.title='COUNTY CLINIC';
  rooms.clinic.w=900;rooms.clinic.h=620;rooms.clinic.spawn={x:450,y:520};rooms.clinic.exit={x:450,y:574};
  rooms.clinic.props=[{x:175,y:145,w:125,h:65,t:'desk'},{x:390,y:150,w:90,h:135,t:'cabinet'},{x:660,y:150,w:110,h:65,t:'table'},{x:220,y:365,w:130,h:55,t:'bed'},{x:600,y:365,w:130,h:55,t:'bed'}];
  rooms.clinic.items=[{x:175,y:185,type:'loot',name:'Clinic medical supplies',loot:'medkit',found:false},{x:660,y:185,type:'loot',name:'Clinic battery crate',loot:'battery',found:false}];
  rooms.depot=structuredClone(rooms.station);
  rooms.depot.title='ROAD MAINTENANCE DEPOT';
  rooms.depot.w=900;rooms.depot.h=620;rooms.depot.spawn={x:450,y:520};rooms.depot.exit={x:450,y:574};
  rooms.depot.props=[{x:170,y:160,w:180,h:65,t:'desk'},{x:440,y:145,w:145,h:110,t:'cabinet'},{x:700,y:160,w:100,h:145,t:'shelves'},{x:250,y:390,w:155,h:70,t:'table'},{x:650,y:390,w:155,h:70,t:'table'}];
  rooms.depot.items=[{x:440,y:280,type:'loot',name:'Road crew ammunition',loot:'ammo',found:false},{x:700,y:335,type:'loot',name:'Road crew batteries',loot:'battery',found:false}];
  rooms.church=structuredClone(rooms.cabin);
  rooms.church.title='ST. MERCY CHAPEL';
  rooms.church.w=860;rooms.church.h=620;rooms.church.spawn={x:430,y:520};rooms.church.exit={x:430,y:574};
  rooms.church.props=[{x:430,y:150,w:190,h:60,t:'table'},{x:200,y:250,w:70,h:120,t:'cabinet'},{x:660,y:250,w:70,h:120,t:'cabinet'},{x:430,y:360,w:220,h:45,t:'table'}];
  rooms.church.items=[{x:430,y:185,type:'loot',name:'Chapel first-aid kit',loot:'medkit',found:false},{x:660,y:315,type:'loot',name:'Chapel emergency batteries',loot:'battery',found:false}];
  rooms.warehouse=structuredClone(rooms.gas);
  rooms.warehouse.title='FLOOD CONTROL WAREHOUSE';
  rooms.warehouse.w=960;rooms.warehouse.h=640;rooms.warehouse.spawn={x:480,y:540};rooms.warehouse.exit={x:480,y:594};
  rooms.warehouse.props=[{x:170,y:150,w:130,h:120,t:'shelves'},{x:380,y:150,w:130,h:120,t:'shelves'},{x:610,y:150,w:130,h:120,t:'shelves'},{x:800,y:150,w:90,h:120,t:'cabinet'},{x:480,y:370,w:180,h:65,t:'table'}];
  rooms.warehouse.items=[{x:800,y:300,type:'loot',name:'Warehouse ammunition',loot:'ammo',found:false},{x:480,y:400,type:'loot',name:'Warehouse medical crate',loot:'medkit',found:false}];
  rooms.farmhouse=structuredClone(rooms.cabin);
  rooms.farmhouse.title='CYPRESS FARMHOUSE';
  rooms.farmhouse.w=900;rooms.farmhouse.h=620;rooms.farmhouse.spawn={x:450,y:520};rooms.farmhouse.exit={x:450,y:574};
  rooms.farmhouse.props=[{x:190,y:155,w:120,h:75,t:'bed'},{x:420,y:150,w:120,h:55,t:'desk'},{x:690,y:160,w:95,h:115,t:'cabinet'},{x:230,y:370,w:150,h:50,t:'table'},{x:670,y:380,w:120,h:50,t:'bed'}];
  rooms.farmhouse.items=[{id:'farmhouse-medkit',x:420,y:180,type:'loot',name:'Farmhouse emergency kit',loot:'medkit',found:false},{id:'farmhouse-ammo',x:690,y:300,type:'loot',name:'Farmhouse spare ammo',loot:'ammo',found:false},{id:'silas-venn',x:500,y:300,type:'witness',name:'Silas Venn — witness',found:state.witnessInterviewed}];
  rooms.station.items.push({id:'anchor-station',x:900,y:520,type:'sideTask',task:'anchor',name:'Black signal seal',detail:'A ring of black wax surrounds a police dispatch chip. The wax is warm and pulses like a slow heartbeat.',found:false});
  rooms.motel.items.push({id:'anchor-motel',x:835,y:470,type:'sideTask',task:'anchor',name:'Motel mirror seal',detail:'A scratched mirror has been sealed to the wall with black wax. Your reflection is still standing after you move.',found:false});
  rooms.church.items.push({id:'anchor-chapel',x:745,y:485,type:'sideTask',task:'anchor',name:'Chapel bell seal',detail:'A strip of black material binds the bell clapper. From inside it, someone quietly repeats your last breath.',found:false});
  const result=structuredClone(rooms[name]||rooms.checkpoint);
  result.id=name;
  for(const item of result.items){
    if(!item.id)item.id=name+'-'+String(item.name||'item').toLowerCase().replace(/[^a-z0-9]+/g,'-');
    const savedState=state.roomItemStates&&state.roomItemStates[item.id];
    if(savedState){item.found=!!savedState.found;item.missing=!!savedState.missing;}
    else if(state.missingIds.includes(item.id))item.missing=true;
  }
  if(name==='farmhouse')for(const item of result.items)if(item.type==='witness')item.found=state.witnessInterviewed&&state.witnessTrust>=2;
  if(name==='station')for(const item of result.items)if(item.type==='intakeDesk')item.found=false;
  return result;
}
function resetGame(){
  const spec=specs[state.selectedCharacter];
  player={x:310,y:330,r:10,angle:0,speed:spec.speed,hp:spec.hp,maxHp:spec.hp,stamina:spec.stamina,maxStamina:spec.stamina,step:0,moving:false,hidden:false,invulnerable:0,flash:0,footstep:0};
  health=player.hp;
  stamina=player.stamina;
  ammo=spec.ammo;
  reserve=spec.reserve;
  evidence=0;
  caseRecords=[];
  state.witnessInterviewed=false;
  state.witnessTrust=0;
  state.stationStage='idle';
  state.stationQueue=[];
  state.stationQueuePosition=0;
  state.stationRetryMode=false;
  state.stationDecisions={};
  state.stationChecks={};
  state.stationChats={};
  state.stationTopics={};
  state.stationManifestEvents={};
  state.stationFeedback='';
  state.stationComplete=false;
  state.stationThreat=0;
  state.stationCorrect=0;
  state.stationProcessed=0;
  state.stationIncidentLogged=false;
  state.stationAuditTrail=[];
  state.extractionStarted=false;
  state.extractionHold=0;
  state.extractionWave1=false;
  state.extractionWave2=false;
  state.extractionWave3=false;
  state.extractionWave4=false;
  state.extractionLastToast=0;
  state.extractionWasOutside=false;
  state.exploredRoomIds=[];
  state.caseComparisons=[];
  state.pendingTheory='';
  state.caseTheory='';
  state.theoryAttempts=0;
  state.interviewStep=0;
  state.interviewAwaitingContinue=false;
  state.interviewChoiceFeedback='';
  state.missingTimer=36;
  state.missingCount=0;
  state.missingIds=[];
  state.roomItemStates={};
  state.disappearanceLog=[];
  state.hideSpotActive=false;
  state.hideSpotName='';
  state.hideRestoreFlashlight=false;
  state.crawlerSearchToastAt=0;
  state.hideElapsed=0;
  state.hideRisk=0;
  state.screamCooldown=0;
  state.screamPulseTimer=0;
  state.screamPulseRadius=0;
  state.helpCooldown=0;
  state.helpTimer=0;
  state.helpCount=0;
  state.shoutCount=0;
  state.hideSearchToastAt=0;
  state.anchorsDestroyed=[];
  state.anchorsDisabled=false;
  state.trueEnding=false;
  state.soundVoidTimer=0;state.soundVoidCooldown=34+Math.random()*13;state.soundVoidTotal=0;
  state.finalManifestStarted=false;
  state.adaptiveHorror={sprintExposure:0,flashlightExposure:0,hideCount:0,radioChoices:0,verifiedCalls:0,shotsAttracted:0};
  state.huntActive=false;state.huntTimer=0;state.huntWarning=0;state.huntsTriggered=0;state.huntsSurvived=0;state.nextHuntAt=43+Math.random()*17;state.huntKind='';
  state.radioIncidentCount=0;state.radioIncidentActive=false;state.radioIncidentTimer=0;state.radioSilenceUntil=0;state.nextRadioIncidentAt=42+Math.random()*13;
  state.falseSignal={active:false,x:0,y:0,timer:0,triggered:false};
  state.trailPhantom={active:false,x:0,y:0,timer:0,cooldown:14+Math.random()*13,total:0,phase:Math.random()*9,kind:'edge'};
  state.realityPulseTimer=0;state.realityPulseCooldown=0;state.realityPulseCount=0;state.lastRealityRoom='';
  $('radioBreachPanel').classList.add('hidden');$('huntBanner').classList.remove('active');$('realityPulse').classList.remove('active');document.body.classList.remove('hunting');
  state.paused=false;
  medkits=1;
  batteryCells=1;
  flashlightBattery=100;
  flashlight=true;
  bullets=[];
  particles=[];
  crawlers=[];
  for(let i=0;i<5;i++){
    crawlers.push({x:760+i*410,y:420+(i%3)*450,r:9,hp:2,speed:70+Math.random()*15,phase:Math.random()*8,alert:false,attack:0,dead:false,hiddenUntil:14});
  }
  monster={x:2800,y:2080,r:15,stun:0,phase:0,active:false,spotted:false,attack:0,lastMove:0,warpCooldown:0,hidden:false,vanishTimer:0,vanishCooldown:4.5+Math.random()*3.4,activeTime:0,pendingX:0,pendingY:0,reappearGlow:0,blinkCount:0};
  makeObjects();
  state.elapsed=0;
  state.missionClock=137;
  state.toastTimer=0;
  state.radioTimer=0;
  state.lightning=0;
  state.lightningNext=9;
  state.screenShake=0;
  state.damageFlash=0;
  state.noise=0;
  state.intensity=0;
  state.exitHintCooldown=0;
  state.apparitionTimer=0;
  state.apparitionCooldown=9+Math.random()*8;
  state.apparitionX=0;
  state.apparitionY=0;
  state.horrorEventFlags={};
  state.storyScareQueue=[];
  state.indoorPresence={timer:0,cooldown:7+Math.random()*5,x:0,y:0,phase:0,arming:0,appearances:0};
  indoorEchoHistory=[];indoorEcho={active:false,timer:0,cooldown:11+Math.random()*5,x:0,y:0,angle:0,phase:Math.random()*9,roomId:'',roomAge:0};indoorEchoSampleTimer=0;indoorEchoRoomId='';
  outdoorEchoTrail=[];outdoorEchoSampleTimer=0;outdoorMemoryEcho={active:false,timer:0,cooldown:31+Math.random()*16,x:0,y:0,angle:0,phase:Math.random()*9,focused:0,seen:false};
  state.deathFade=0;
  state.victoryFade=0;
  state.discovered=0;
  state.rescued=0;
  state.keysFound=false;
  state.exploredRooms=0;
  state.kills=0;
  state.shots=0;
  state.saves=0;
  state.floor='outside';
  state.room=null;
  state.prologueStage='call';
  state.prologueTimer=0;
  state.driveProgress=0;
  state.driveSpeed=0;
  state.driveLane=0;
  state.driveScroll=0;
  state.driveShake=0;
  state.driveSirenPhase=0;
  state.driveNearMissTimer=0;
  state.drivePassedCars=0;
  state.driveCollisionCooldown=0;
  state.driveCrashTimer=0;
  state.driveDamage=0;
  state.driveCollisionCount=0;
  state.lastBuildingExit=null;
  state.sceneFade=0;
  state.horrorBeat=0;
  state.voiceCaptionTimer=0;
  state.voiceCooldown=0;
  state.voiceAmbientTimer=13+Math.random()*8;
  state.voiceEventFlags={};
  $('voiceSubtitle').className='';
  $('voiceWords').textContent='';
  if('speechSynthesis' in window)window.speechSynthesis.cancel();
  state.personalScareTimer=0;
  state.personalScareCooldown=0;
  state.personalScareCount=0;
  state.threatTier=0;
  state.flashlightFlickerTimer=0;
  state.storyScareQueue=[];
  state.indoorPresence={timer:0,cooldown:7+Math.random()*5,x:0,y:0,phase:0,arming:0,appearances:0};
  $('personalScare').classList.remove('active','variant-personnel','variant-contact','variant-duplicate','variant-address');
  $('personalScare').setAttribute('aria-hidden','true');
  state.gameOver=false;
  state.reloadActive=false;
  state.won=false;
  state.paused=false;
  state.running=true;
  stamina=player.stamina;
  health=player.hp;
  camera={x:0,y:0};
  lastSafe={x:player.x,y:player.y};
  footstepTimer=0;
  attackTimer=0;
  shootTimer=0;
  reloadTimer=0;
  interactCooldown=0;
  damageCooldown=0;
  growlTimer=5;
  ambientTimer=0;
  initializeAssets();
  lastMiniDraw=-999;lastMiniFloor=null;lastMiniRoom=null;
  interiorBaseCache={room:null,canvas:null};
  $('officerName').textContent=spec.name.replace(/^Officer\s+/i,'').toUpperCase();
  resetPartnerChat();
  $('hud').style.display='block';
  document.body.classList.add('game-active','prologue-mode','prologue-call');
  applyControlMode();
  setScreen('game');
  updateHUD();
  updateObjectives();
  audioStart();
  setAmbientBed(true);
  tone(280,.15,'sine',.08,160);
  state.lastFrame=performance.now();
  requestAnimationFrame(loop);
}
function applyControlMode(){
  document.body.classList.toggle('mobile-mode',state.controlMode==='mobile');
  $('desktopMode').classList.toggle('selected',state.pendingMode==='desktop');
  $('mobileMode').classList.toggle('selected',state.pendingMode==='mobile');
}
function activeOverlay(){
  return ['menu','character','controls','how','credits','account','objectives','inventory','pause','ending','radio'].includes(state.screen);
}
function setPrologueStage(stage){
  state.prologueStage=stage;
  state.prologueTimer=0;
  document.body.classList.toggle('prologue-call',stage==='call');
  document.body.classList.toggle('prologue-drive',stage==='drive');
  document.body.classList.toggle('prologue-arrival',stage==='arrival');
  document.body.classList.toggle('prologue-mode',stage!=='swamp');
  if(stage==='drive'){if(!state.partnerSent||Object.keys(state.partnerSent).length===0)resetPartnerChat();state.driveProgress=0;state.driveSpeed=0;state.driveLane=0;state.driveScroll=0;state.driveShake=0;state.driveSirenPhase=0;state.driveNearMissTimer=0;state.drivePassedCars=0;state.driveCollisionCooldown=1.2;state.driveCrashTimer=0;state.driveDamage=0;state.driveCollisionCount=0;state.driveWheel=0;state.driveGear=1;state.driveRpm=900;state.driveWiper=0;state.driveSkid=0;state.driveHydroplane=0;tone(540,.18,'sawtooth',.06,-210);toast('DISPATCH: Proceed to mile marker nine. You are the only available unit.',4);}
  if(stage==='arrival'){state.driveSpeed=0;sound('radio');tone(76,.75,'triangle',.08,-34);}
}
function acceptDispatch(){
  if(state.prologueStage!=='call')return;
  audioStart();
  enterNightSearch();
}
function enterNightSearch(){
  if(state.prologueStage==='swamp')return;
  keys={};
  touchRun=false;
  pointer.down=false;
  setPrologueStage('swamp');
  const safeSpawns=[{x:520,y:500},{x:500,y:480},{x:550,y:520},{x:470,y:465},{x:560,y:545},{x:430,y:450}];
  let spawn=safeSpawns.find(point=>!blockedAt(point.x,point.y,player.r));
  if(!spawn)spawn={x:520,y:500};
  player.x=spawn.x;player.y=spawn.y;player.angle=.9;player.moving=false;player.step=0;
  camera.x=clamp(player.x-W/2,0,WORLD.w-W);
  camera.y=clamp(player.y-H/2,0,WORLD.h-H);
  lastSafe={x:player.x,y:player.y};
  state.elapsed=0;state.horrorBeat=0;state.lightningNext=3.2;state.sceneFade=.9;
  state.threatTier=0;
  state.flashlightFlickerTimer=0;
  updateHUD();updateObjectives();
  toast('MILE MARKER 9. YOU ARE ON FOOT. THE ONLY FOOTPRINTS IN THE MUD ARE YOURS — UNTIL THEY ARE NOT.',5.2);
  partnerExchange('survivorSignalBriefing','I have two weak bodycam heat signatures. Mara is near the ranger station; Eli is further along the southeast trail. Green SOS markers should show their positions. The dispatch system says you are the only living officer on the channel.','Copy. I will follow the green markers. If you hear my voice, verify it is actually me.');
  tone(48,.9,'triangle',.085,-22);
}
function exitPatrolCar(){enterNightSearch();}
function driveTrafficLane(i){
  const offsets=[.015,-.02,.035,-.035,.005,.025,-.015,.04,-.03,.01,-.025,.03];
  return (i%3===0?.25:-.25)+offsets[i];
}
function currentDriveLane(){
  return .25+state.driveLane*.48;
}
function partnerOfficerKey(){return state.selectedCharacter==='yumi'?'hugo':'yumi';}
function partnerOfficerName(){return specs[partnerOfficerKey()].name;}
function resetPartnerChat(){
  state.partnerSent={};
  state.partnerChatCount=0;
  const title=$('partnerTitle');
  const box=$('partnerMessages');
  if(title)title.textContent=partnerOfficerName().toUpperCase()+' // SECURE CHAT';
  if(box)box.replaceChildren();
  addPartnerMessage('Secure channel connected. I’m staying on your line.','incoming');
}
function addPartnerMessage(message,side='incoming'){
  const box=$('partnerMessages');
  if(!box)return;
  const row=document.createElement('div');
  row.className='partner-message '+(side==='outgoing'?'outgoing':side==='unknown'?'unknown':'incoming');
  const sender=document.createElement('span');
  sender.className='partner-sender';
  sender.textContent=side==='outgoing'?'YOU':side==='unknown'?'UNKNOWN CALLSIGN // UNVERIFIED':partnerOfficerName().toUpperCase();
  const copy=document.createElement('span');
  copy.textContent=message;
  row.append(sender,copy);
  box.appendChild(row);
  while(box.children.length>5)box.removeChild(box.firstElementChild);
  box.scrollTop=box.scrollHeight;
  state.partnerChatCount++;
}
function partnerExchange(key,incoming,outgoing){
  if(state.partnerSent[key])return;
  state.partnerSent[key]=true;
  addPartnerMessage(incoming,'incoming');
  if(outgoing)setTimeout(()=>{
    if(state.running&&!state.gameOver)addPartnerMessage(outgoing,'outgoing');
  },850);
}
function partnerReplyFor(message){
  const text=message.toLowerCase();
  if(/\b(help|scared|afraid|panic|hurt|injured)\b/.test(text))return 'Stay with me. Press H for a short signal pulse if you need help. Find cover with C, but keep still—your breathing is coming through the line.';
  if(/\b(hide|hiding|closet|cabinet|table)\b/.test(text))return 'Use C near a cabinet, bed, table, shelves, tree, or reeds. Stay still and keep quiet. If it starts searching the same spot, leave before your breath gives you away.';
  if(/\b(scream|shout|yell)\b/.test(text))return 'G will let you scream. It may stagger nearby crawlers, but it will tell the Smiler exactly where you are. Do not use it when you need silence.';
  if(/\b(anchor|seal|motel mirror|chapel)\b/.test(text))return 'I found references to three signal anchors: the police station, Pine Rest Motel, and St. Mercy Chapel. Break all three if you want to weaken the extraction and unlock the true ending.';
  if(/\b(where|location|position|map)\b/.test(text))return 'Your signal is moving even when the map says you’re standing still. Follow the evidence markers and don’t trust the minimap blindly.';
  if(/\b(backup|police|dispatch|unit)\b/.test(text))return 'Dispatch says you are still the only unit assigned to this call. I’m checking the roster again. Please don’t answer any other voice using our call signs.';
  if(/\b(smiler|monster|creature|thing|figure|someone|person)\b/.test(text))return 'Don’t approach it. Keep distance and use the light only when you need to. If it stops moving, that does not mean it is gone.';
  if(/\b(car|drive|traffic|road|crash|lane|speed)\b/.test(text))return 'There are no vehicles on this assignment. Follow the footpath, stay near the flashlight beam, and watch for a shape that copies your movement.';
  if(/\b(evidence|clue|file|case)\b/.test(text))return 'Copy. Log everything you find, but don’t read the personnel details over the radio. The file system has been showing records that do not exist.';
  if(/\b(hello|hey|hi|you there|copy)\b/.test(text))return 'I’m here. Radio is clear on my end, although I keep hearing your microphone open when you are not speaking.';
  if(/\b(trust|fake|real|you)\b/.test(text))return 'Listen carefully: I will never ask you for your real name, address, or personal details. If a message asks for that, it is not me.';
  return 'Received. I’m still here on the secure channel. Keep moving, keep your flashlight ready, and tell me if you see another figure.';
}
function sendPartnerChat(){
  if(state.radioSilenceUntil>state.elapsed){toast('CHANNEL CUT. RADIO RETURNS IN '+Math.ceil(state.radioSilenceUntil-state.elapsed)+'s.',1.8);return;}
  const input=$('partnerInput');
  if(!input)return;
  const message=input.value.trim();
  if(!message)return;
  if(!state.running||state.gameOver){toast('CHAT CHANNEL IS NOT ACTIVE.',1.3);return;}
  if(!['call','drive','arrival','swamp'].includes(state.prologueStage)){toast('WAIT UNTIL THE DISPATCH CALL CONNECTS.',1.4);return;}
  input.value='';
  addPartnerMessage(message,'outgoing');
  const reply=partnerReplyFor(message);
  window.setTimeout(()=>{
    if(state.running&&!state.gameOver)addPartnerMessage(reply,'incoming');
  },450+Math.random()*550);
}
function updatePartnerChat(){
  const stage=state.prologueStage;
  if(stage==='drive'){
    const p=state.driveProgress;
    if(p>=7)partnerExchange('drive7','You good? Dispatch says you’re the only unit heading out. Watch the standing water.','Copy. I’m rolling to Mile Marker 9.');
    if(p>=21)partnerExchange('drive21','My map shows two patrol units under your call sign. You should only be seeing one.','I’m the only one on this trail.');
    if(p>=39)partnerExchange('drive39','Your breathing is coming through my radio, but you are not speaking.','My flashlight is shaking, but nothing is in front of me.');
    if(p>=60)partnerExchange('drive60','Don’t stop for anyone standing on the shoulder. Especially anyone in uniform.','Who else would be out here?');
    if(p>=81)partnerExchange('drive81','Bodycam feed just caught someone directly behind you. Keep moving. Don’t look.','There is nobody behind me. I am not looking.');
  }else if(stage==='arrival'){
    if(state.prologueTimer>2.5)partnerExchange('arrival2','I just lost your bodycam feed. I can still hear your breathing, but the picture is gone.','Stay on the line. I’m stepping into the woods now.');
  }else if(stage==='swamp'){
    if(state.elapsed>5.2)partnerExchange('swamp5','Your bodycam shows a second figure following your steps. It stops every time you turn around.','I’m looking at the treeline. There’s nothing there.');
    if(state.elapsed>16)partnerExchange('swamp16','That voice on channel two isn’t me. I haven’t said a word for the last minute.','Then who keeps answering my radio?');
    if(evidence>=1)partnerExchange('evidence1','I’m getting text from the case file. It says “stop trusting the person on this chat.”','Is that supposed to be a joke?');
    if(evidence>=3)partnerExchange('evidence3','I can see your flashlight on the live feed. There is a second beam moving beside yours.','I only have one flashlight.');
    if(state.rescued>=1)partnerExchange('rescued1','The survivor’s file says they were rescued here years ago. Their name is on a report dated tomorrow.','I’m bringing them out. Keep the channel open.');
  }
}
function updateDriveLaneHUD(){
  const value=currentDriveLane();
  const marker=$('laneMarker');
  const label=$('driveLaneLabel');
  const advice=$('laneAdvice');
  if(marker){marker.style.left=(clamp((value+.5),0,1)*100)+'%';marker.style.background=value<.1?'#ff796e':value>.405?'#ff796e':'#fff4bc';}
  let text='RIGHT / TRAVEL LANE',tip='Keep to the right of the double yellow lines.',color='#e3dfc3';
  if(value<-.12){text='ONCOMING LANE';tip='DANGER: steer right immediately to avoid head-on traffic.';color='#f17669';}
  else if(value<.10){text='CROSSING CENTERLINE';tip='Move right. The double yellow lines are directly beneath you.';color='#f0c56f';}
  else if(value>.405){text='RIGHT SHOULDER';tip='You are drifting off the road. Steer left gently.';color='#f17669';}
  else if(state.driveNearMissTimer>0){text='RIGHT LANE · CLOSE PASS';tip='Traffic passed close by. Hold your lane.';color='#f0d48c';}
  if(label){label.textContent=text;label.style.color=color;}
  if(advice)advice.textContent=tip;
}
function updatePrologue(dt){
  state.prologueTimer+=dt;
  updatePersonalScare(dt);
  updateWhispers(dt);
  if(state.prologueStage==='drive'){
    const forward=keys.w||keys.arrowup;
    const brake=keys.s||keys.arrowdown;
    const steer=(keys.d||keys.arrowright?1:0)-(keys.a||keys.arrowleft?1:0);
    state.driveWheel+=(steer-state.driveWheel)*Math.min(1,dt*5.8);
    const integrity=Math.max(0,100-state.driveDamage);
    const handling=Math.max(.42,1-state.driveDamage*.0044);
    if(forward){
      const acceleration=state.driveSpeed<32?21:state.driveSpeed<68?15.5:state.driveSpeed<96?10:5.5;
      state.driveSpeed=Math.min(Math.max(35,124-state.driveDamage*.48),state.driveSpeed+acceleration*dt*(1-state.driveDamage*.004));
    }else{
      state.driveSpeed=Math.max(0,state.driveSpeed-(state.driveSpeed>70?3.2:5.4)*dt);
    }
    if(brake)state.driveSpeed=Math.max(0,state.driveSpeed-(state.driveSpeed>45?58:42)*dt);
    state.driveLane=clamp(state.driveLane+state.driveWheel*dt*(.11+state.driveSpeed*.0032)*handling,-1.3,1.0);
    const playerLane=currentDriveLane();
    const curve=Math.sin(state.driveScroll*.0012+.9)*.20+Math.sin(state.driveScroll*.00047+2.2)*.10;
    if(state.driveSpeed>58&&Math.abs(curve)>.17&&Math.abs(state.driveWheel)<.15){
      state.driveLane=clamp(state.driveLane+curve*dt*.055,-1.3,1.0);
    }
    state.driveScroll+=dt*(9+state.driveSpeed*2.25);
    state.driveSirenPhase+=dt;
    state.driveNearMissTimer=Math.max(0,state.driveNearMissTimer-dt);
    state.driveShake=Math.max(0,state.driveShake-dt*2.5);
    state.driveWiper+=dt*(forward?1.08:.72);
    state.driveSkid=Math.max(0,state.driveSkid-dt*1.8);
    state.driveHydroplane=Math.max(0,state.driveHydroplane-dt*.22);
    if(Math.abs(playerLane)>.405){
      state.driveSpeed=Math.max(15,state.driveSpeed-(brake?8:19)*dt);
      state.driveShake=Math.min(1,state.driveShake+dt*.72);
      state.driveSkid=Math.min(1,state.driveSkid+dt*.65);
      if(Math.random()<dt*.65)tone(88,.07,'square',.018,-18);
    }
    state.driveCollisionCooldown=Math.max(0,state.driveCollisionCooldown-dt);
    state.driveCrashTimer=Math.max(0,state.driveCrashTimer-dt);
    for(let i=0;i<12;i++){
      const direction=i%3===0?1:-1;
      const phase=((i*.137+state.driveScroll*(direction>0?.00052:-.00031))%1+1)%1;
      const z=.035+phase*.91;
      const lane=driveTrafficLane(i);
      if(z>.79&&z<.985&&Math.abs(lane-playerLane)<.125&&state.driveCollisionCooldown<=0&&state.driveSpeed>18){
        state.driveCollisionCooldown=3.2;
        state.driveCrashTimer=1.65;
        state.driveCollisionCount++;
        state.driveDamage=Math.min(100,state.driveDamage+Math.max(14,state.driveSpeed*.30));
        state.driveSpeed=Math.max(0,state.driveSpeed-38);
        state.driveProgress=Math.max(0,state.driveProgress-1.1);
        state.driveShake=1;
        state.driveNearMissTimer=0;
        state.driveSkid=.9;
        sound('hurt');
        tone(47,.48,'sawtooth',.19,-22);
        tone(930,.06,'square',.04,-620);
        toast(state.driveCollisionCount===1?'IMPACT! You struck a vehicle. Brake and steer clear.':'MAJOR COLLISION! Vehicle control compromised.',3.2);
      }else if(z>.76&&z<.95&&Math.abs(lane-playerLane)<.18&&state.driveSpeed>36){
        state.driveNearMissTimer=Math.max(state.driveNearMissTimer,.55);
      }
    }
    if((playerLane>.49||playerLane<-.49)&&state.driveCollisionCooldown<=0&&state.driveSpeed>20){
      state.driveCollisionCooldown=2.7;
      state.driveCrashTimer=1.0;
      state.driveCollisionCount++;
      state.driveDamage=Math.min(100,state.driveDamage+12+state.driveSpeed*.06);
      state.driveSpeed=Math.max(12,state.driveSpeed-26);
      state.driveShake=.9;
      state.driveSkid=1;
      tone(72,.23,'square',.12,-32);
      toast('ROAD EDGE IMPACT! Correct your steering.',2.6);
    }
    if(state.driveSpeed>90&&Math.abs(state.driveWheel)>.78){
      state.driveHydroplane=Math.min(1,state.driveHydroplane+dt*.9);
      state.driveLane=clamp(state.driveLane+state.driveWheel*dt*.16,-1.3,1.0);
    }
    if(state.driveHydroplane>.6){
      state.driveShake=Math.max(state.driveShake,.12);
      if(Math.random()<dt*.15)toast('AQUAPLANING — EASE OFF THE THROTTLE.',1.2);
    }
    if(state.driveDamage>=82&&Math.random()<dt*.24&&state.driveSpeed>72)state.driveSpeed=Math.max(32,state.driveSpeed-8);
    if(state.driveProgress>24&&!state.horrorEventFlags.firstRoadWarning){state.horrorEventFlags.firstRoadWarning=true;state.driveShake=Math.max(state.driveShake,.16);voiceNoise(choose(['left','right']),.08);}
    if(state.driveProgress>66&&!state.horrorEventFlags.secondRoadWarning){state.horrorEventFlags.secondRoadWarning=true;state.driveShake=Math.max(state.driveShake,.24);}
    const gearCuts=[0,17,34,56,81,105];
    const previousGear=state.driveGear;
    state.driveGear=state.driveSpeed<17?1:state.driveSpeed<34?2:state.driveSpeed<56?3:state.driveSpeed<81?4:5;
    if(previousGear!==state.driveGear&&state.prologueTimer>.45){
      tone(state.driveGear>previousGear?176:126,.075,'square',.018,state.driveGear>previousGear?80:-45);
      state.driveShake=Math.max(state.driveShake,.035);
    }
    const low=gearCuts[state.driveGear-1],high=gearCuts[state.driveGear]||124;
    state.driveRpm=850+clamp((state.driveSpeed-low)/Math.max(1,high-low),0,1)*5000+(forward?420:0);
    if(brake&&state.driveSpeed<8)state.driveRpm=780;
    state.driveProgress+=dt*(.20+state.driveSpeed*.047)*(Math.abs(playerLane)>.43?.64:1);
    const trafficCycle=Math.floor(state.driveScroll/270);
    if(trafficCycle>state.drivePassedCars&&state.driveSpeed>30){
      state.drivePassedCars=trafficCycle;
      if(Math.random()<.72){
        state.driveShake=Math.max(state.driveShake,.09);
        tone(Math.random()<.5?118:172,.1,'triangle',.022,-42);
        if(Math.random()<.34)toast(choose(['A SEMI TRUCK THUNDERS PAST IN THE RAIN.','ONCOMING HEADLIGHTS BLOOM THROUGH THE SPRAY.','WATER SHEETS ACROSS THE WINDSHIELD.','A DRIVER LOOKS STRAIGHT AT YOU.','THE ROAD BENDS SHARPLY AHEAD.']),1.65);
      }
    }
    if(state.prologueTimer>7&&state.prologueTimer<7.08)sound('radio');
    if(state.driveDamage>=82&&state.prologueTimer%7<dt)toast('VEHICLE CRITICAL: STEER GENTLY AND AVOID IMPACTS.',2.2);
    if(state.driveProgress>=100){state.driveProgress=100;setPrologueStage('arrival');}
  }
  for(const r of raindrops){r.y+=r.speed*dt*.65;r.x-=r.speed*.16*dt;if(r.y>H+15){r.y=-15;r.x=Math.random()*W;}if(r.x<-15)r.x=W+10;}
  state.sceneFade=Math.max(0,state.sceneFade-dt*1.7);
  updatePartnerChat();
  if(state.prologueStage==='drive')updateDriveLaneHUD();
}
function poly(points,color){ctx.fillStyle=color;ctx.beginPath();ctx.moveTo(points[0][0],points[0][1]);for(let i=1;i<points.length;i++)ctx.lineTo(points[i][0],points[i][1]);ctx.closePath();ctx.fill();}
function strokePoly(points,color,width=1){ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();ctx.moveTo(points[0][0],points[0][1]);for(let i=1;i<points.length;i++)ctx.lineTo(points[i][0],points[i][1]);ctx.closePath();ctx.stroke();}
function drawRadioScreen(x,y,w,h,active){
  px(x,y,w,h,'#070c09');px(x+3,y+3,w-6,h-6,'#17271c');px(x+7,y+7,w-14,h-14,'#09150e');
  ctx.fillStyle=active?'#b9c9a0':'#7a8876';ctx.font='bold 10px monospace';ctx.textAlign='left';ctx.fillText(active?'FSP DISPATCH':'NO SIGNAL',x+10,y+17);
  for(let i=0;i<14;i++){const hh=2+Math.abs(Math.sin(state.prologueTimer*5+i*1.4))*(active?12:3);px(x+10+i*5,y+h-11-hh,3,hh,active?'#789d72':'#354437');}
  px(x+w-18,y+9,4,4,active?'#bf5149':'#3a463b');
}
function drawPrologueCall(){
  px(0,0,W,H,'#000000');
  const sky=ctx.createLinearGradient(0,0,0,H*.68);
  sky.addColorStop(0,'#010302');
  sky.addColorStop(.58,'#050907');
  sky.addColorStop(1,'#000000');
  ctx.fillStyle=sky;
  ctx.fillRect(0,0,W,H);
  const horizon=H*.43;
  for(let i=0;i<45;i++){
    const x=(i*83)%Math.max(1,W);
    const height=72+(i*47)%Math.max(80,Math.floor(H*.42));
    const width=12+(i*17)%42;
    const sway=Math.sin(state.prologueTimer*.4+i)*2;
    px(x+sway,horizon-height,width,height,'#020403');
    px(x-5+sway,horizon-height*.61,width+10,height*.12,'#030604');
    px(x-9+sway,horizon-height*.39,width+18,height*.09,'#010302');
  }
  poly([[0,horizon],[W*.12,H*.48],[W*.29,H*.41],[W*.41,H*.47],[W*.58,H*.40],[W*.77,H*.47],[W,H*.43],[W,H],[0,H]],'#010201');
  poly([[W*.33,H],[W*.44,H*.53],[W*.56,H*.53],[W*.72,H],[W,H],[0,H]],'#020403');
  for(let i=0;i<70;i++){
    const x=(i*137+Math.sin(state.prologueTimer*.7+i)*9)%Math.max(1,W);
    const y=(i*61+state.prologueTimer*(i%3===0?1.3:0.2))%Math.max(1,H);
    const a=.08+(i%5)*.025;
    ctx.fillStyle='rgba(137,151,126,'+a+')';
    ctx.fillRect(x,y,1+(i%7===0?1:0),1);
  }
  const fog=ctx.createRadialGradient(W*.5,H*.61,8,W*.5,H*.61,Math.max(W,H)*.72);
  fog.addColorStop(0,'rgba(12,19,13,.19)');
  fog.addColorStop(.48,'rgba(2,5,3,.21)');
  fog.addColorStop(1,'rgba(0,0,0,.98)');
  ctx.fillStyle=fog;
  ctx.fillRect(0,0,W,H);
  const pxp=W*.5,pyp=H*.70;
  ctx.fillStyle='#000';
  ctx.beginPath();
  ctx.moveTo(pxp-15,pyp-30);ctx.lineTo(pxp+13,pyp-30);ctx.lineTo(pxp+19,pyp+10);ctx.lineTo(pxp+10,pyp+40);ctx.lineTo(pxp+5,pyp+76);ctx.lineTo(pxp-6,pyp+76);ctx.lineTo(pxp-10,pyp+40);ctx.lineTo(pxp-20,pyp+10);ctx.closePath();ctx.fill();
  px(pxp-11,pyp-50,22,23,'#000');
  px(pxp-7,pyp-43,4,2,'#8e171d');px(pxp+4,pyp-43,4,2,'#8e171d');
  drawRadioScreen(W*.065,H*.73,W*.23,H*.105,true);
  const pw=Math.min(720,W-34),ph=Math.min(235,H*.38),bx=(W-pw)/2,by=H*.075;
  px(bx-3,by-3,pw+6,ph+6,'#000');px(bx,by,pw,ph,'rgba(0,0,0,.97)');
  strokePoly([[bx,by],[bx+pw,by],[bx+pw,by+ph],[bx,by+ph]],'#3c4937',1);
  px(bx+17,by+17,4,ph-34,'#8d2728');
  ctx.textAlign='left';ctx.fillStyle='#899681';ctx.font='bold 12px monospace';ctx.fillText('INCOMING DISPATCH // PRIORITY CALL',bx+34,by+31);
  ctx.fillStyle='#e5e6dc';ctx.font='bold '+Math.max(16,Math.min(24,W*.026))+'px monospace';ctx.fillText('MILE MARKER 9 — OFFICER NEEDS ASSISTANCE',bx+34,by+67);
  ctx.fillStyle='#8f9c8a';ctx.font=Math.max(11,Math.min(15,W*.015))+'px monospace';ctx.fillText('The unit is gone. The road is empty. The radio is not.',bx+34,by+99);ctx.fillText('You must continue on foot. No backup will be sent.',bx+34,by+121);
  ctx.fillStyle='#d4b878';ctx.font='bold '+Math.max(11,Math.min(14,W*.014))+'px monospace';ctx.fillText('DISPATCH: “Keep the light on. Do not answer yourself.”',bx+34,by+155);
  ctx.fillStyle='#aeb9a7';ctx.font='11px monospace';ctx.fillText('A second breath is audible on the channel.',bx+34,by+178);
  const blink=Math.floor(state.prologueTimer*1.6)%2===0;ctx.textAlign='center';ctx.fillStyle=blink?'#eee0b6':'#646c5e';ctx.font='bold '+Math.max(12,Math.min(16,W*.017))+'px monospace';ctx.fillText('PRESS E / ENTER OR TAP TO ENTER THE WOODS',W/2,by+ph-18);
  drawVignette();
}
function drawTrafficCars(horizon,roadCenter,topHalf,bottomHalf,city){
  for(let i=0;i<12;i++){
    const direction=i%3===0?1:-1;
    const phase=((i*.137+state.driveScroll*(direction>0?.00052:-.00031))%1+1)%1;
    const z=.035+phase*.91;
    const y=horizon+Math.pow(z,1.82)*(H-horizon);
    const half=topHalf+(bottomHalf-topHalf)*Math.pow(z,.86);
    const curve=(Math.sin(state.driveScroll*.0012+.9)*.20+Math.sin(state.driveScroll*.00047+2.2)*.10)*W*(1-z);
    const lane=driveTrafficLane(i);
    const playerLane=currentDriveLane();
    const x=W*.5-playerLane*half+curve+(lane-playerLane)*half+playerLane*half;
    const depth=.17+z*1.24;
    const truck=i%6===0;
    const suv=!truck&&i%4===1;
    const cw=(truck?20:suv?17:13)+z*(truck?82:suv?72:64);
    const ch=5+z*(truck?39:suv?34:29);
    if(y<H*.39||y>H+ch||x<-cw*2||x>W+cw*2)continue;
    const top=y-ch*.83,bottom=y+ch*.39;
    ctx.save();
    ctx.globalAlpha=.52+z*.48;
    ctx.fillStyle='rgba(0,0,0,.58)';ctx.beginPath();ctx.ellipse(x,y+ch*.35,cw*.66,ch*.46,0,0,Math.PI*2);ctx.fill();
    if(truck){
      const trailerY=top-ch*.52;
      poly([[x-cw*.43,trailerY],[x+cw*.43,trailerY],[x+cw*.46,top+ch*.02],[x-cw*.46,top+ch*.02]],i%2?'#4c514b':'#55594e');
      px(x-cw*.35,trailerY+3,cw*.70,Math.max(2,ch*.08),'#737568');
      for(let seam=1;seam<5;seam++)px(x-cw*.4+cw*.16*seam,trailerY+4,1,Math.max(2,ch*.43),'#303933');
      px(x-cw*.48,top+ch*.01,cw*.96,ch*.30,'#222b28');
    }
    const body=i%5===0?'#66645a':i%3===0?'#303d42':i%2===0?'#414943':'#62625b';
    poly([[x-cw*.45,top+ch*.28],[x-cw*.37,top+ch*.02],[x-cw*.24,top],[x+cw*.24,top],[x+cw*.38,top+ch*.06],[x+cw*.46,top+ch*.28],[x+cw*.43,bottom],[x-cw*.43,bottom]],body);
    poly([[x-cw*.30,top+ch*.20],[x-cw*.19,top+ch*.04],[x+cw*.19,top+ch*.04],[x+cw*.30,top+ch*.20]],direction>0?'#263b3b':'#9da99a');
    px(x-cw*.24,top+ch*.22,cw*.48,Math.max(2,ch*.055),'#18201f');
    px(x-cw*.31,top+ch*.31,cw*.62,Math.max(2,ch*.06),'#2b3431');
    px(x-cw*.40,top+ch*.48,Math.max(2,cw*.11),Math.max(2,ch*.18),'#202623');
    px(x+cw*.29,top+ch*.48,Math.max(2,cw*.11),Math.max(2,ch*.18),'#202623');
    px(x-cw*.45,top+ch*.74,cw*.90,Math.max(2,ch*.11),'#222724');
    if(truck){
      px(x-cw*.44,bottom-ch*.05,cw*.88,Math.max(2,ch*.10),'#1c211f');
      px(x-cw*.38,bottom-ch*.12,Math.max(2,cw*.13),Math.max(2,ch*.10),direction>0?'#ef554b':'#eee1ba');
      px(x+cw*.25,bottom-ch*.12,Math.max(2,cw*.13),Math.max(2,ch*.10),direction>0?'#ef554b':'#eee1ba');
    }
    if(direction>0){
      const glow=ctx.createRadialGradient(x,bottom-ch*.13,1,x,bottom-ch*.13,cw*.56);
      glow.addColorStop(0,'rgba(255,48,39,.42)');glow.addColorStop(1,'rgba(255,35,27,0)');ctx.fillStyle=glow;ctx.fillRect(x-cw*.62,bottom-ch*.4,cw*1.24,ch*.85);
      px(x-cw*.37,bottom-ch*.17,Math.max(2,cw*.14),Math.max(2,ch*.18),'#f05248');px(x+cw*.23,bottom-ch*.17,Math.max(2,cw*.14),Math.max(2,ch*.18),'#f05248');
      px(x-cw*.26,bottom-ch*.04,cw*.52,Math.max(2,ch*.06),'#85877b');
      if(z>.5){ctx.fillStyle='rgba(208,220,205,'+(.025+z*.04)+')';ctx.beginPath();ctx.moveTo(x-cw*.42,bottom);ctx.lineTo(x-cw*.85,bottom+ch*.34);ctx.lineTo(x+cw*.85,bottom+ch*.34);ctx.lineTo(x+cw*.42,bottom);ctx.closePath();ctx.fill();}
    }else{
      const glow=ctx.createRadialGradient(x,top+ch*.39,1,x,top+ch*.39,cw*.88);
      glow.addColorStop(0,'rgba(245,245,207,.43)');glow.addColorStop(.30,'rgba(224,235,203,.16)');glow.addColorStop(1,'rgba(224,239,215,0)');ctx.fillStyle=glow;ctx.fillRect(x-cw*1.1,top-ch*.12,cw*2.2,ch*1.85);
      poly([[x-cw*.38,top+ch*.35],[x-cw*.20,top+ch*.27],[x-cw*.05,top+ch*.27],[x-cw*.05,top+ch*.40],[x-cw*.39,top+ch*.43]],'#d9dbb9');
      poly([[x+cw*.05,top+ch*.27],[x+cw*.20,top+ch*.27],[x+cw*.38,top+ch*.35],[x+cw*.39,top+ch*.43],[x+cw*.05,top+ch*.40]],'#d9dbb9');
      const beam=ctx.createLinearGradient(x,top+ch*.4,x,y+ch*1.25);beam.addColorStop(0,'rgba(245,242,201,.14)');beam.addColorStop(1,'rgba(241,243,211,0)');ctx.fillStyle=beam;ctx.beginPath();ctx.moveTo(x-cw*.27,top+ch*.4);ctx.lineTo(x-cw*1.45,y+ch*1.15);ctx.lineTo(x+cw*1.45,y+ch*1.15);ctx.lineTo(x+cw*.27,top+ch*.4);ctx.closePath();ctx.fill();
      px(x-cw*.39,top+ch*.32,Math.max(2,cw*.15),Math.max(2,ch*.20),'#f1edc8');px(x+cw*.24,top+ch*.32,Math.max(2,cw*.15),Math.max(2,ch*.20),'#f1edc8');
      px(x-cw*.35,top+ch*.58,cw*.70,Math.max(2,ch*.06),'#1b2422');
    }
    if(suv){px(x-cw*.12,top+ch*.02,cw*.24,Math.max(2,ch*.05),'#8f9a89');px(x-cw*.28,top+ch*.23,cw*.56,Math.max(2,ch*.06),'#252f2b');}
    if(z>.68&&state.driveSpeed>35){ctx.globalAlpha=.13;for(let spray=0;spray<4;spray++){const sx=x+(spray-1.5)*cw*.34;px(sx,bottom+spray*2,Math.max(2,cw*.12),Math.max(2,ch*.07),'#a6b7ad');}}
    ctx.restore();
  }
}
function drawDrivingPoliceLights(){
  const phase=state.driveSirenPhase*16;
  const redOn=Math.sin(phase)>0;
  ctx.save();
  const red=ctx.createRadialGradient(W*.08,H*.43,0,W*.08,H*.43,W*.46);
  red.addColorStop(0,redOn?'rgba(255,25,33,.23)':'rgba(255,28,34,.015)');red.addColorStop(.55,'rgba(210,28,40,.045)');red.addColorStop(1,'rgba(255,28,34,0)');
  ctx.fillStyle=red;ctx.fillRect(0,H*.10,W*.57,H*.70);
  const blue=ctx.createRadialGradient(W*.92,H*.43,0,W*.92,H*.43,W*.46);
  blue.addColorStop(0,!redOn?'rgba(35,104,255,.25)':'rgba(40,105,255,.012)');blue.addColorStop(.55,'rgba(38,84,210,.045)');blue.addColorStop(1,'rgba(40,105,255,0)');
  ctx.fillStyle=blue;ctx.fillRect(W*.43,H*.10,W*.57,H*.70);
  ctx.globalAlpha=.12+.18*Math.abs(Math.sin(phase));
  poly([[W*.04,H*.42],[W*.18,H*.48],[W*.39,H*.69],[W*.16,H*.64]],redOn?'#be3036':'#314f9b');
  poly([[W*.96,H*.42],[W*.82,H*.48],[W*.61,H*.69],[W*.84,H*.64]],redOn?'#294c9c':'#b9333a');
  const barY=H*.705;px(W*.427,barY,W*.060,H*.012,redOn?'#fa5149':'#2e65dc');px(W*.513,barY,W*.060,H*.012,redOn?'#2e65dc':'#fa5149');
  ctx.globalAlpha=.92;px(W*.437,barY+2,W*.037,2,redOn?'#ffb7a4':'#9cc8ff');px(W*.526,barY+2,W*.037,2,redOn?'#9cc8ff':'#ffb7a4');
  ctx.restore();
}
function drawDriveRainAndGlass(){
  ctx.save();
  ctx.strokeStyle='rgba(193,212,207,.23)';ctx.lineWidth=1;ctx.beginPath();
  for(let i=0;i<145;i++){
    const x=(i*137+state.driveScroll*4.0+(i%5)*state.driveSpeed*.08)%W;
    const y=(i*71+state.driveScroll*5.9)%(H*.735);
    const len=10+(i%6)*2+state.driveSpeed*.025;
    ctx.moveTo(x,y);ctx.lineTo(x-4-len*.1,y+len);
  }
  ctx.stroke();
  ctx.strokeStyle='rgba(189,207,198,.10)';ctx.lineWidth=2;
  for(let i=0;i<7;i++){
    const x=(i*W*.19+Math.sin(state.prologueTimer*.7+i)*W*.07+state.driveScroll*.15)%W;
    ctx.beginPath();ctx.moveTo(x,H*.10);ctx.quadraticCurveTo(x-W*.04,H*.29,x-W*.085,H*.57);ctx.stroke();
  }
  const wipe=Math.sin(state.driveWiper*1.2)*.94;
  ctx.save();ctx.translate(W*.5,H*.72);ctx.rotate(-.35+wipe*.46);ctx.globalAlpha=.32;ctx.strokeStyle='#aab8b0';ctx.lineWidth=Math.max(2,W*.003);ctx.beginPath();ctx.moveTo(-W*.35,0);ctx.quadraticCurveTo(0,-H*.045,W*.32,-H*.03);ctx.stroke();ctx.restore();
  ctx.globalAlpha=.17;ctx.fillStyle='#c5d2c8';ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(W*.16,0);ctx.lineTo(W*.34,H*.69);ctx.lineTo(W*.16,H*.69);ctx.closePath();ctx.fill();ctx.beginPath();ctx.moveTo(W,0);ctx.lineTo(W*.84,0);ctx.lineTo(W*.66,H*.69);ctx.lineTo(W*.84,H*.69);ctx.closePath();ctx.fill();
  ctx.restore();
}
function drawDriveSideStreets(horizon,roadCenter,topHalf,bottomHalf,city){
  const ground=city?'#272d2a':'#162119';
  for(let i=0;i<(city?4:2);i++){
    let z=((i*.29+state.driveScroll*.00043+.12)%1);
    if(z<.12)z+=.12;
    const y=horizon+z*z*(H-horizon);
    const cx=roadCenter+(W*.5-roadCenter)*z;
    const half=topHalf+(bottomHalf-topHalf)*z;
    const thick=5+z*38;
    const spread=W*(city?.09:.05)+z*W*(city?.29:.16);
    for(const side of [-1,1]){
      const edge=cx+side*half;
      const far=edge+side*spread;
      poly([[edge,y-thick*.48],[far,y-thick*1.3],[far+side*(7+z*12),y+thick*1.4],[edge,y+thick*.48]],'#0b100e');
      poly([[edge+side*2,y-thick*.35],[far-side*2,y-thick],[far-side*2,y+thick],[edge+side*2,y+thick*.35]],ground);
      if(city&&z>.31){
        for(let k=0;k<5;k++){
          const sx=edge+side*(spread*(.24+k*.12));
          const sy=y+Math.sin(k*2+i)*thick*.22;
          px(sx,sy,Math.max(2,z*5),Math.max(2,z*3),'#a4a18a');
        }
        if(i%2===0){
          const poleX=far-side*(z*3+2);px(poleX,y-thick*2.3,Math.max(2,z*3),thick*2.3,'#161e1b');
          px(poleX-side*4,y-thick*2.5,Math.max(4,z*9),Math.max(3,z*7),i%4===0?'#a5423d':'#a8b08c');
          const glow=ctx.createRadialGradient(poleX,y-thick*2.5,1,poleX,y-thick*2.5,15+z*65);glow.addColorStop(0,'rgba(198,176,112,.22)');glow.addColorStop(1,'rgba(198,176,112,0)');ctx.fillStyle=glow;ctx.fillRect(poleX-55,y-thick*2.5-55,110,110);
        }
      }
    }
    if(city&&z>.45&&z<.98){
      const crossY=y-thick*.12;
      for(let k=-3;k<=3;k++){
        const sx=cx+k*(5+z*10);
        px(sx,crossY,Math.max(2,z*4),Math.max(2,z*4),'#aaa68e');
      }
    }
  }
  if(city){
    for(const side of [-1,1]){
      for(let i=0;i<5;i++){
        const z=((i*.23+state.driveScroll*.00031+.07)%1);
        const y=horizon+z*z*(H-horizon);
        const cx=roadCenter+(W*.5-roadCenter)*z;
        const half=topHalf+(bottomHalf-topHalf)*z;
        const x=cx+side*(half+W*(.08+z*.14));
        const lampY=y-z*H*.045;
        if(x>-25&&x<W+25){
          px(x,y-z*45,Math.max(2,z*3),z*45,'#151d1a');px(x-side*z*8,lampY,Math.max(5,z*15),Math.max(2,z*5),'#9d9b80');
          const glow=ctx.createRadialGradient(x-side*z*6,lampY,1,x-side*z*6,lampY,8+z*45);glow.addColorStop(0,'rgba(218,193,133,.3)');glow.addColorStop(1,'rgba(218,193,133,0)');ctx.fillStyle=glow;ctx.fillRect(x-z*48,lampY-z*45,z*96,z*90);
        }
      }
    }
  }
}
function drawDrivePixelDetails(horizon,centerAt,halfAt,yAt,city,suburb){
  const speedRatio=clamp(state.driveSpeed/125,0,1);
  ctx.save();
  ctx.globalCompositeOperation='screen';
  const beamStrength=.045+speedRatio*.13;
  const leftBeam=ctx.createLinearGradient(W*.31,H*.73,W*.42,H*.28);
  leftBeam.addColorStop(0,'rgba(215,229,195,'+beamStrength+')');
  leftBeam.addColorStop(.42,'rgba(188,211,190,'+(beamStrength*.58)+')');
  leftBeam.addColorStop(1,'rgba(165,196,181,0)');
  poly([[W*.24,H*.96],[centerAt(.95)-halfAt(.95)*.12,yAt(.95)],[centerAt(.08)-halfAt(.08)*.14,yAt(.08)],[W*.42,H*.73]],leftBeam);
  const rightBeam=ctx.createLinearGradient(W*.69,H*.73,W*.58,H*.28);
  rightBeam.addColorStop(0,'rgba(215,229,195,'+beamStrength+')');
  rightBeam.addColorStop(.42,'rgba(188,211,190,'+(beamStrength*.58)+')');
  rightBeam.addColorStop(1,'rgba(165,196,181,0)');
  poly([[W*.76,H*.96],[centerAt(.95)+halfAt(.95)*.12,yAt(.95)],[centerAt(.08)+halfAt(.08)*.14,yAt(.08)],[W*.58,H*.73]],rightBeam);
  ctx.restore();
  for(let i=0;i<115;i++){
    const z=((i/115+state.driveScroll*.0017)%1);
    const y=yAt(z),c=centerAt(z),half=halfAt(z);
    const grain=seeded(i+Math.floor(state.driveScroll/12),Math.floor(z*120));
    const x=c+(grain-.5)*half*1.6;
    if(x>c-half*.92&&x<c+half*.92){
      const size=1+z*2.2;
      const toneValue=(i%4===0)?'rgba(175,188,165,.20)':'rgba(9,13,12,.26)';
      px(x,y,size,size,toneValue);
    }
  }
  for(let i=0;i<22;i++){
    const z=((i/22+state.driveScroll*.0048)%1);
    const y=yAt(z),c=centerAt(z),half=halfAt(z);
    const width=1+z*4,height=1+z*5;
    for(const side of [-1,1]){
      const x=c+side*half*.965;
      px(x-width/2,y-height/2,width,height,i%3===0?'#d4d7ba':'#7b8a7c');
      if(!city&&z>.2){
        const postX=c+side*(half+W*(.013+z*.015));
        px(postX-width/2,y-z*17,width,Math.max(2,z*18),'#303a30');
        if(i%2===0)px(postX-width,y-z*19,width*2,Math.max(2,z*4),'#9eac97');
      }
    }
  }
  if(city){
    const z=.61,y=yAt(z),c=centerAt(z),half=halfAt(z);
    for(const side of [-1,1]){
      const poleX=c+side*(half+W*.11);
      if(poleX>-80&&poleX<W+80){
        px(poleX-2,y-H*.19,4,H*.19,'#161e1b');
        px(poleX-15,y-H*.20,30,5,'#303a32');
        const signal= Math.floor(state.driveScroll*.018+side+z)%3;
        px(poleX-10,y-H*.196,5,5,signal===0?'#d44740':'#4e5b49');
        px(poleX-2,y-H*.196,5,5,signal===1?'#d7bd6e':'#4e5b49');
        px(poleX+6,y-H*.196,5,5,signal===2?'#c8423d':'#4e5b49');
      }
    }
  }
  ctx.save();
  if(speedRatio>.42){
    ctx.strokeStyle='rgba(193,211,204,'+(.025+speedRatio*.045)+')';
    ctx.lineWidth=1;
    for(let i=0;i<24;i++){
      const sx=((i*97+state.driveScroll*7)%W);
      const sy=H*(.40+((i*31)%52)/100);
      const len=8+speedRatio*(24+(i%5)*11);
      ctx.beginPath();ctx.moveTo(sx,sy);ctx.lineTo(sx-(sx-W*.5)*.025,sy+len);ctx.stroke();
    }
  }
  ctx.restore();
  const glint=ctx.createLinearGradient(0,H*.64,0,H*.91);
  glint.addColorStop(0,'rgba(198,218,203,0)');
  glint.addColorStop(.65,'rgba(166,189,178,'+(.025+speedRatio*.055)+')');
  glint.addColorStop(1,'rgba(211,219,191,'+(.04+speedRatio*.06)+')');
  ctx.fillStyle=glint;ctx.fillRect(W*.27,H*.63,W*.46,H*.31);
}
function drawDriveDashboardDetails(){
  const radius=Math.max(11,Math.min(22,W*.027));
  const cy=H*.839;
  const dials=[{x:W*.445,value:clamp(state.driveSpeed/135,0,1),label:'MPH',color:'#b6c99e'},{x:W*.555,value:clamp((state.driveRpm-800)/5200,0,1),label:'RPM',color:state.driveRpm>5000?'#d75a4e':'#c6b77d'}];
  for(const dial of dials){
    ctx.fillStyle='#050806';ctx.beginPath();ctx.arc(dial.x,cy,radius+3,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle='#697567';ctx.lineWidth=2;ctx.beginPath();ctx.arc(dial.x,cy,radius,Math.PI*.78,Math.PI*2.22);ctx.stroke();
    ctx.strokeStyle='#9da88c';ctx.lineWidth=1;
    for(let i=0;i<9;i++){const a=Math.PI*.78+i/8*Math.PI*1.44;ctx.beginPath();ctx.moveTo(dial.x+Math.cos(a)*(radius-3),cy+Math.sin(a)*(radius-3));ctx.lineTo(dial.x+Math.cos(a)*(radius-1),cy+Math.sin(a)*(radius-1));ctx.stroke();}
    const needle=Math.PI*.78+dial.value*Math.PI*1.44;
    ctx.strokeStyle=dial.color;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(dial.x,cy);ctx.lineTo(dial.x+Math.cos(needle)*(radius-4),cy+Math.sin(needle)*(radius-4));ctx.stroke();
    ctx.fillStyle='#d2d7c5';ctx.font='bold 7px monospace';ctx.textAlign='center';ctx.fillText(dial.label,dial.x,cy+radius+8);
  }
  const lampY=H*.879;
  for(let i=0;i<5;i++){
    const on=i===0?state.driveDamage>45:i===1?state.driveHydroplane>.28:i===2?state.driveSpeed>105:i===3?state.driveSpeed<8:state.driveCollisionCount>0;
    px(W*.402+i*W*.018,lampY,Math.max(3,W*.006),3,on?(i===1?'#dfb75f':'#c64a42'):'#283329');
  }
  ctx.fillStyle='#7f8a79';ctx.font='7px monospace';ctx.textAlign='left';ctx.fillText('BELT  ABS  ENG  BRAKE  WARN',W*.40,H*.899);
}
function drawDriveScene(){
  const progress=state.driveProgress/100;
  const city=progress<.39;
  const suburb=progress>=.39&&progress<.68;
  const playerLane=currentDriveLane();
  const sky=ctx.createLinearGradient(0,0,0,H*.66);
  sky.addColorStop(0,city?'#07121e':suburb?'#091317':'#020604');
  sky.addColorStop(.42,city?'#1b303a':suburb?'#1c2c2b':'#101a13');
  sky.addColorStop(1,city?'#48534b':suburb?'#343f32':'#1b291b');
  ctx.fillStyle='#080d0b';ctx.fillRect(0,0,W,H);ctx.fillStyle=sky;ctx.fillRect(0,0,W,H*.70);
  const horizon=H*.355+Math.sin(state.driveScroll*.0021)*2.5;
  const flash=Math.max(0,Math.sin(state.driveSirenPhase*1.7)-.86);
  if(flash>.02){ctx.fillStyle='rgba(147,181,181,'+flash*.12+')';ctx.fillRect(0,0,W,H*.63);}
  const skyline=ctx.createLinearGradient(0,horizon-H*.17,0,horizon+H*.12);skyline.addColorStop(0,'rgba(4,9,11,.08)');skyline.addColorStop(1,'rgba(5,9,8,.8)');ctx.fillStyle=skyline;ctx.fillRect(0,horizon-H*.18,W,H*.36);
  for(let i=0;i<(city?46:suburb?34:27);i++){
    const layerSpeed=.16+(i%7)*.065;
    let layer=(i*97-state.driveScroll*layerSpeed)%(W+230);if(layer<0)layer+=W+230;
    const x=layer-115;const bw=25+(i*23)%98;const hh=28+(i*47)%Math.max(68,H*.38);const y=horizon-hh;
    if(city||suburb){
      const base=city?(i%5===0?'#202f33':i%3===0?'#142428':'#192b2e'):(i%4===0?'#26322b':i%3===0?'#1a2925':'#20302a');
      px(x-3,y-4,bw+6,hh+5,'#080d0e');px(x,y,bw,hh,base);px(x+3,y+4,bw-6,3,city?'#354648':'#323c30');
      if(i%4===0){px(x+bw*.62,y-9,bw*.25,10,'#344443');px(x+bw*.7,y-17,2,8,'#54615b');}
      for(let wy=y+10;wy<horizon-6;wy+=12){
        px(x+4,wy,bw-8,1,'#283b39');
        for(let wx=x+6;wx<x+bw-5;wx+=12){
          const lit=seeded(i,Math.floor(wy+wx))>(suburb?.66:.47);
          if(lit){const flick=Math.sin(state.driveScroll*.031+i+wx*.3)>.89;px(wx,wy,4,5,flick?'#c6a96e':((i+Math.floor(wx/11))%4===0?'#80a19b':'#858e72'));}
        }
      }
      if(i%7===0){px(x+bw*.17,y+hh*.66,bw*.66,hh*.19,'#0a1410');px(x+bw*.21,y+hh*.69,bw*.58,hh*.1,'#4a5545');px(x+bw*.28,y+hh*.71,bw*.42,Math.max(2,hh*.035),'#c1a76d');}
      if(i%9===0){px(x+bw*.25,y-12,bw*.5,8,'#070b09');px(x+bw*.27,y-10,bw*.46,3,'#c2463f');}
      if(i%11===0&&x>-120&&x<W+120){px(x+bw*.18,y+hh*.44,bw*.64,hh*.05,'#303a31');px(x+bw*.22,y+hh*.47,bw*.56,hh*.03,'#b5a16c');}
    }else{
      px(x+10,horizon-35,6,35,'#151d14');px(x,horizon-65,bw,37,'#101a12');px(x+5,horizon-80,bw-10,24,'#0b150e');px(x+13,horizon-94,bw-26,17,'#111c13');
      if(i%4===0){px(x+bw*.28,horizon-73,4,6,'#c0a269');px(x+bw*.64,horizon-73,4,6,'#b84f43');}
    }
  }
  for(let layer=0;layer<3;layer++){
    const speed=.11+layer*.08;
    ctx.globalAlpha=.20+layer*.07;
    for(let i=0;i<22;i++){
      let x=(i*73-state.driveScroll*speed*(1+layer*.3))%(W+100);if(x<0)x+=W+100;x-=50;
      const yy=horizon+H*(.04+layer*.06)+Math.sin(i*2.2+state.driveScroll*.002)*H*.012;
      if(city){px(x,yy,8+layer*4,2+layer,'#76847b');}else{px(x,yy,3+layer*2,H*(.04+layer*.015),'#111b12');px(x-7,yy+4,15+layer*3,5+layer*2,'#17251a');}
    }
  }
  ctx.globalAlpha=1;
  const topHalf=W*.070,bottomHalf=W*.475;
  const roadCurve=(Math.sin(state.driveScroll*.00115+.8)*.19+Math.sin(state.driveScroll*.00048+2.3)*.105)*W;
  const centerAt=z=>W*.5-playerLane*(topHalf+(bottomHalf-topHalf)*Math.pow(z,.86))+roadCurve*(1-z);
  const yAt=z=>horizon+Math.pow(z,1.82)*(H-horizon);
  const halfAt=z=>topHalf+(bottomHalf-topHalf)*Math.pow(z,.86);
  const segments=34;
  const leftShoulder=[],rightShoulder=[];
  for(let i=0;i<=segments;i++){const z=i/segments;const c=centerAt(z),h=halfAt(z);leftShoulder.push([c-h-W*.035*z,yAt(z)]);}
  for(let i=segments;i>=0;i--){const z=i/segments;const c=centerAt(z),h=halfAt(z);rightShoulder.push([c+h+W*.035*z,yAt(z)]);}
  poly(leftShoulder.concat(rightShoulder),'#131a15');
  const roadPoly=[];
  for(let i=0;i<=segments;i++){const z=i/segments;roadPoly.push([centerAt(z)-halfAt(z),yAt(z)]);}
  for(let i=segments;i>=0;i--){const z=i/segments;roadPoly.push([centerAt(z)+halfAt(z),yAt(z)]);}
  poly(roadPoly,'#252c2b');
  const wet=ctx.createLinearGradient(0,horizon,0,H);wet.addColorStop(0,'rgba(99,122,120,.02)');wet.addColorStop(.45,'rgba(118,145,141,.12)');wet.addColorStop(1,'rgba(156,171,158,.19)');
  ctx.save();ctx.beginPath();ctx.moveTo(centerAt(0)-halfAt(0),yAt(0));for(let i=1;i<=segments;i++)ctx.lineTo(centerAt(i/segments)-halfAt(i/segments),yAt(i/segments));for(let i=segments;i>=0;i--)ctx.lineTo(centerAt(i/segments)+halfAt(i/segments),yAt(i/segments));ctx.closePath();ctx.fillStyle=wet;ctx.fill();ctx.restore();
  ctx.strokeStyle='#596057';ctx.lineWidth=2;ctx.beginPath();for(let i=0;i<=segments;i++){const z=i/segments;const x=centerAt(z)-halfAt(z);if(i===0)ctx.moveTo(x,yAt(z));else ctx.lineTo(x,yAt(z));}for(let i=segments;i>=0;i--){const z=i/segments;ctx.lineTo(centerAt(z)+halfAt(z),yAt(z));}ctx.stroke();
  for(let i=0;i<26;i++){
    const z=((i/26+state.driveScroll*.009)%1);const y=yAt(z);const half=halfAt(z);const c=centerAt(z);const dashH=2+z*24;const dashW=1+z*2;
    if(i%2===0){
      const lineGap=3+z*8;
      const lineWidth=1.4+z*3.0;
      const lineHeight=2+z*28;
      px(c-lineGap-lineWidth-1,y-lineHeight*.5,lineWidth+2,lineHeight,'#211f17');
      px(c+lineGap-1,y-lineHeight*.5,lineWidth+2,lineHeight,'#211f17');
      px(c-lineGap-lineWidth*.20,y-lineHeight*.5,lineWidth*.76,lineHeight,'#ffe88b');
      px(c+lineGap+lineWidth*.24,y-lineHeight*.5,lineWidth*.76,lineHeight,'#ffe88b');
      if((city||suburb)&&z>.28){
        px(c-half*.49,y-lineHeight*.44,Math.max(1,z*2),lineHeight*.88,'rgba(219,226,206,.45)');
        px(c+half*.49,y-lineHeight*.44,Math.max(1,z*2),lineHeight*.88,'rgba(219,226,206,.45)');
      }
    }
    const edgeWidth=1+z*3;
    if(i%2===0){px(c-half*.98,y-dashH*.5,edgeWidth,dashH,'#b7c3b5');px(c+half*.98-edgeWidth,y-dashH*.5,edgeWidth,dashH,'#b7c3b5');}
    if(city&&i%3===0){px(c-half*.50,y-dashH*.36,Math.max(1,dashW*.6),dashH*.7,'#888e7c');px(c+half*.50,y-dashH*.36,Math.max(1,dashW*.6),dashH*.7,'#888e7c');}
  }
  for(const side of [-1,1]){
    for(let i=0;i<8;i++){
      const z=((i/8+state.driveScroll*.0036)%1);const y=yAt(z);const h=halfAt(z);const c=centerAt(z);const x=c+side*(h+W*(.025+z*.025));
      if(x<-35||x>W+35)continue;
      if(city||suburb){
        const poleH=H*(.012+z*.07);px(x-2-z*2,y-poleH,3+z*4,poleH,'#1a221f');px(x-side*z*7,y-poleH,Math.max(4,z*17),Math.max(2,z*4),'#a9a083');
        const glow=ctx.createRadialGradient(x-side*z*5,y-poleH,1,x-side*z*5,y-poleH,12+z*65);glow.addColorStop(0,'rgba(229,203,143,.34)');glow.addColorStop(1,'rgba(229,203,143,0)');ctx.fillStyle=glow;ctx.fillRect(x-z*65,y-poleH-z*58,z*130,z*116);
      }else{
        px(x-2-z*2,y-H*(.02+z*.08),3+z*5,H*(.02+z*.08),'#101710');px(x-11*z,y-H*(.105+z*.04),24*z,16*z,'#122016');px(x-15*z,y-H*(.065+z*.04),30*z,12*z,'#17271b');
      }
      if(i%3===0){px(x-side*(5+z*10),y,Math.max(2,z*7),Math.max(2,z*5),'#9c8e68');}
    }
  }
  if(city||suburb){
    const signalX=centerAt(.35)-halfAt(.35)*.95;const signalY=yAt(.35)-H*.08;
    if(signalX>-40&&signalX<W+40){px(signalX-3,signalY,6,H*.08,'#171d1a');px(signalX-10,signalY-5,20,Math.max(14,H*.045),'#262d28');px(signalX-7,signalY-2,5,5,Math.sin(state.driveScroll*.025)>0?'#b83e3c':'#4d292a');px(signalX+2,signalY+5,5,5,'#c8a35b');}
  }else{
    const signZ=.28;const signX=centerAt(signZ)-halfAt(signZ)-W*.045;const signY=yAt(signZ)-H*.04;
    if(signX>-W*.1&&signX<W*1.1){px(signX,signY,Math.max(3,W*.004),H*.045,'#242a25');px(signX-W*.055,signY-H*.012,W*.105,H*.032,'#22382d');ctx.strokeStyle='#b3bb9d';ctx.lineWidth=1;ctx.strokeRect(signX-W*.055,signY-H*.012,W*.105,H*.032);ctx.fillStyle='#d2d6be';ctx.font='bold '+Math.max(8,W*.010)+'px monospace';ctx.textAlign='center';ctx.fillText('MILE 9',signX,signY+H*.009);}
  }
  drawTrafficCars(horizon,centerAt(1),topHalf,bottomHalf,city||suburb);
  drawDrivePixelDetails(horizon,centerAt,halfAt,yAt,city,suburb);
  const beam=ctx.createRadialGradient(W*.5,H*.65,5,W*.5,H*.75,H*.72);beam.addColorStop(0,'rgba(231,228,190,.20)');beam.addColorStop(.28,'rgba(209,215,189,.105)');beam.addColorStop(1,'rgba(218,226,210,0)');ctx.fillStyle=beam;ctx.fillRect(0,H*.28,W,H*.72);
  for(let i=0;i<17;i++){const z=((i/17+state.driveScroll*.017)%1);const y=yAt(z);const c=centerAt(z);const h=halfAt(z);const puddleW=(4+z*34);const x=c+Math.sin(i*7.3+state.driveScroll*.004)*h*.48;px(x-puddleW/2,y,puddleW,Math.max(1,z*4),'rgba(163,180,169,.23)');}
  drawDrivingPoliceLights();
  drawDriveRainAndGlass();
  const shake=state.driveShake*(2.0+state.driveSpeed*.025);ctx.save();ctx.translate((Math.random()-.5)*shake,(Math.random()-.5)*shake+Math.sin(state.driveScroll*.04)*state.driveSpeed*.009);
  poly([[0,H*.79],[W*.12,H*.70],[W*.32,H*.68],[W*.68,H*.68],[W*.88,H*.70],[W,H*.79],[W,H],[0,H]],'#070a08');
  poly([[0,H*.82],[W*.16,H*.74],[W*.35,H*.72],[W*.65,H*.72],[W*.84,H*.74],[W,H*.82],[W,H],[0,H]],'#202720');
  for(let i=0;i<30;i++){const x=i*W/30;px(x,H*.80,Math.max(2,W*.004),Math.max(2,H*.004),i%2?'#30382e':'#181f19');}
  poly([[0,H*.91],[W*.17,H*.78],[W*.35,H*.75],[W*.65,H*.75],[W*.83,H*.78],[W,H*.91],[W,H],[0,H]],'#111612');
  px(W*.07,H*.80,W*.24,H*.12,'#10150f');px(W*.075,H*.805,W*.23,H*.105,'#1c251b');
  for(let i=0;i<8;i++){px(W*.085+i*W*.027,H*.817,Math.max(2,W*.008),2,'#2f382a');px(W*.085+i*W*.027,H*.835,Math.max(2,W*.008),2,'#151d16');}
  px(W*.375,H*.79,W*.25,H*.105,'#080c0a');px(W*.386,H*.802,W*.228,H*.081,'#1a241c');px(W*.399,H*.812,W*.20,H*.009,'#48503b');px(W*.399,H*.834,W*.10,H*.006,'#a18c5e');px(W*.52,H*.834,W*.075,H*.006,'#a18c5e');
  px(W*.696,H*.795,W*.24,H*.125,'#080b09');px(W*.708,H*.808,W*.216,H*.098,'#1a211b');
  ctx.fillStyle='#b6c9a6';ctx.textAlign='center';ctx.font='bold '+Math.max(16,Math.min(30,W*.033))+'px monospace';ctx.fillText(Math.round(state.driveSpeed),W*.82,H*.855);ctx.fillStyle='#778b75';ctx.font='bold '+Math.max(8,Math.min(11,W*.012))+'px monospace';ctx.fillText('MPH',W*.82,H*.875);ctx.fillStyle='#d1bb78';ctx.font='bold '+Math.max(9,Math.min(12,W*.013))+'px monospace';ctx.fillText('D'+state.driveGear,W*.75,H*.835);
  ctx.fillStyle='#677863';ctx.fillRect(W*.735,H*.888,W*.17,3);ctx.fillStyle=state.driveRpm>5100?'#d55247':'#c2b77c';ctx.fillRect(W*.735,H*.888,W*.17*clamp((state.driveRpm-800)/5200,0,1),3);ctx.fillStyle='#8d9984';ctx.font='8px monospace';ctx.fillText('RPM',W*.91,H*.896);
  ctx.save();ctx.translate(W*.5,H*.965);ctx.rotate(state.driveWheel*.54);ctx.strokeStyle='#080b09';ctx.lineWidth=Math.max(12,W*.018);ctx.beginPath();ctx.arc(0,0,Math.min(W,H)*.145,Math.PI*1.07,Math.PI*1.93);ctx.stroke();ctx.strokeStyle='#50584c';ctx.lineWidth=3;ctx.beginPath();ctx.arc(0,0,Math.min(W,H)*.145,Math.PI*1.07,Math.PI*1.93);ctx.stroke();ctx.strokeStyle='#222920';ctx.lineWidth=Math.max(6,W*.008);ctx.beginPath();ctx.moveTo(0,-Math.min(W,H)*.08);ctx.lineTo(0,Math.min(W,H)*.018);ctx.moveTo(-Math.min(W,H)*.09,Math.min(W,H)*.01);ctx.lineTo(Math.min(W,H)*.09,Math.min(W,H)*.01);ctx.stroke();ctx.restore();
  const sirenRed=Math.sin(state.driveSirenPhase*16)>0;px(W*.43,H*.72,W*.06,H*.018,sirenRed?'#f04e47':'#315dcb');px(W*.51,H*.72,W*.06,H*.018,sirenRed?'#315dcb':'#f04e47');
  drawRadioScreen(W*.055,H*.755,W*.20,H*.085,state.driveProgress<75);
  drawDriveDashboardDetails();
  ctx.restore();
  const barW=Math.min(500,W*.54),barX=(W-barW)/2,barY=H*.075;px(barX-8,barY-10,barW+16,60,'rgba(3,7,5,.86)');ctx.strokeStyle='#47574b';ctx.strokeRect(barX-8,barY-10,barW+16,60);ctx.fillStyle='#bfc8b3';ctx.font='bold 12px monospace';ctx.textAlign='left';ctx.fillText('ROUTE 9  /  DISPATCH DESTINATION',barX,barY+7);px(barX,barY+18,barW,9,'#263129');px(barX+2,barY+20,(barW-4)*progress,5,progress>.82?'#b34a43':'#b6b17a');ctx.fillStyle='#e5e2d4';ctx.textAlign='right';ctx.fillText(Math.floor(progress*100)+'%',barX+barW,barY+7);
  ctx.textAlign='center';ctx.fillStyle=playerLane>.43||playerLane<-.43?'#e86c62':state.driveNearMissTimer>0?'#e6d391':'#d8ddce';ctx.font='bold '+Math.max(11,Math.min(15,W*.016))+'px monospace';ctx.fillText(playerLane>.43||playerLane<-.43?'WARNING: ROAD EDGE':state.driveNearMissTimer>0?'CLOSE PASS — KEEP YOUR LANE':state.driveSpeed<4?'HOLD W / UP TO START MOVING':'W/↑ ACCELERATE   S/↓ BRAKE   A/D STEER',W/2,H*.615);
  updateDriveLaneHUD();
  const integrity=Math.max(0,100-state.driveDamage);px(W*.72,H*.86,W*.20,6,'#090e0b');px(W*.72+2,H*.86+2,W*.196*(integrity/100),2,integrity<35?'#d34a42':integrity<65?'#c2a65e':'#829b76');ctx.textAlign='left';ctx.fillStyle=integrity<35?'#ef7268':'#b6c3a8';ctx.font='bold 9px monospace';ctx.fillText('VEHICLE CONDITION '+Math.round(integrity)+'%',W*.72,H*.855);
  if(state.driveSkid>.05){ctx.fillStyle='rgba(190,207,195,'+state.driveSkid*.12+')';ctx.fillRect(0,H*.52,W,H*.28);}
  if(state.driveCrashTimer>0){
    const alpha=Math.min(.42,state.driveCrashTimer*.29);ctx.fillStyle='rgba(150,12,16,'+alpha+')';ctx.fillRect(0,0,W,H);
    ctx.strokeStyle='rgba(229,232,219,'+Math.min(.8,state.driveCrashTimer*.7)+')';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(W*.82,H*.15);ctx.lineTo(W*.73,H*.29);ctx.lineTo(W*.78,H*.37);ctx.lineTo(W*.67,H*.52);ctx.moveTo(W*.73,H*.29);ctx.lineTo(W*.59,H*.23);ctx.moveTo(W*.78,H*.37);ctx.lineTo(W*.9,H*.44);ctx.moveTo(W*.67,H*.52);ctx.lineTo(W*.61,H*.7);ctx.stroke();
    px(W*.29,H*.34,W*.42,58,'rgba(3,6,5,.92)');ctx.strokeStyle='#b94742';ctx.strokeRect(W*.29,H*.34,W*.42,58);ctx.textAlign='center';ctx.fillStyle='#f0c4a5';ctx.font='bold '+Math.max(16,Math.min(24,W*.027))+'px monospace';ctx.fillText('COLLISION — REGAIN CONTROL',W*.5,H*.34+24);ctx.fillStyle='#d9d8c7';ctx.font='12px monospace';ctx.fillText('Ease off the gas, brake, and steer back to your lane.',W*.5,H*.34+44);
  }
  if(state.driveHydroplane>.15){ctx.fillStyle='rgba(189,205,198,'+state.driveHydroplane*.12+')';ctx.fillRect(0,H*.30,W,H*.40);}
  if(state.driveDamage>15){
    const crackAlpha=clamp((state.driveDamage-12)/95,.12,.78);
    const cx=W*(.69+(state.driveCollisionCount%3)*.045),cy=H*(.42+(state.driveCollisionCount%2)*.08);
    ctx.save();ctx.globalAlpha=crackAlpha;ctx.strokeStyle='#d5ded4';ctx.lineWidth=1;
    for(let branch=0;branch<9;branch++){
      const a=branch*Math.PI*2/9+(state.driveCollisionCount*.19);const length=(18+(branch%4)*11)*(.55+state.driveDamage/70);
      let x=cx,y=cy;ctx.beginPath();ctx.moveTo(x,y);
      for(let step=0;step<4;step++){
        x+=Math.cos(a+(step%2?-.15:.17))*length/4;
        y+=Math.sin(a+(step%2?-.15:.17))*length/4;
        ctx.lineTo(Math.round(x),Math.round(y));
      }
      ctx.stroke();
    }
    px(cx-2,cy-2,4,4,'#e8eee1');
    ctx.restore();
  }
  drawVignette();
}
function drawArrivalScene(){
  px(0,0,W,H,'#040706');const grad=ctx.createLinearGradient(0,0,0,H);grad.addColorStop(0,'#07100d');grad.addColorStop(.68,'#0d1710');grad.addColorStop(1,'#030504');ctx.fillStyle=grad;ctx.fillRect(0,0,W,H);
  for(let i=0;i<22;i++){const x=(i*79)%W;const ht=H*(.18+((i*17)%47)/100);px(x,H*.53-ht*.4,8+(i%5)*7,ht,'#0a120c');px(x-8,H*.48-ht*.25,24+(i%4)*8,10,'#0b150e');px(x-4,H*.41-ht*.2,18,12,'#0e1a11');}
  poly([[W*.37,H*.4],[W*.63,H*.4],[W*.95,H],[W*.05,H]],'#090d0a');poly([[W*.46,H*.4],[W*.54,H*.4],[W*.68,H],[W*.32,H]],'#171d17');ctx.setLineDash([18,22]);ctx.strokeStyle='#655f4a';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(W*.5,H*.41);ctx.lineTo(W*.5,H);ctx.stroke();ctx.setLineDash([]);
  const cx=W*.35,cy=H*.66;const sirenRed=Math.sin(state.prologueTimer*13)>0;ctx.save();ctx.translate(cx,cy);ctx.rotate(-.10);px(-W*.12,-H*.06,W*.24,H*.13,'#080a08');px(-W*.105,-H*.055,W*.21,H*.105,'#a6aaa0');px(-W*.082,-H*.047,W*.164,H*.085,'#263a36');px(-W*.07,-H*.04,W*.14,H*.07,'#111e1b');px(-W*.04,-H*.035,W*.08,H*.06,'#07100d');px(-W*.1,-H*.055,W*.05,H*.014,'#c9c8b5');px(W*.05,-H*.055,W*.05,H*.014,'#c9c8b5');px(-W*.025,-H*.048,W*.05,H*.018,'#eee8d0');px(-W*.105,H*.03,W*.036,H*.018,'#c8443b');px(W*.069,H*.03,W*.036,H*.018,'#c8443b');px(-W*.045,-H*.069,W*.035,H*.012,sirenRed?'#fb4844':'#255bd4');px(W*.01,-H*.069,W*.035,H*.012,sirenRed?'#255bd4':'#fb4844');ctx.restore();
  const patrolGlow=ctx.createRadialGradient(cx,H*.68,2,cx,H*.68,W*.48);patrolGlow.addColorStop(0,sirenRed?'rgba(226,34,42,.20)':'rgba(35,82,213,.20)');patrolGlow.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=patrolGlow;ctx.fillRect(0,H*.3,W,H*.65);
  const flashX=sirenRed?W*.17:W*.79;const flashGlow=ctx.createRadialGradient(flashX,H*.64,2,flashX,H*.64,W*.32);flashGlow.addColorStop(0,sirenRed?'rgba(240,50,47,.22)':'rgba(45,100,230,.22)');flashGlow.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=flashGlow;ctx.fillRect(0,H*.35,W,H*.65);
  ctx.strokeStyle='rgba(163,180,177,.30)';ctx.lineWidth=1;ctx.beginPath();for(const drop of raindrops){ctx.moveTo(drop.x,drop.y);ctx.lineTo(drop.x-4,drop.y+11);}ctx.stroke();
  const ox=W*.62,oy=H*.64;px(ox-8,oy-42,16,18,'#101511');px(ox-11,oy-23,22,37,'#1f2c23');px(ox-18,oy-21,7,27,'#151e18');px(ox+11,oy-21,7,27,'#151e18');px(ox-8,oy+10,7,22,'#121813');px(ox+2,oy+10,7,22,'#121813');px(ox-9,oy-45,18,6,'#756b49');
  ctx.save();ctx.globalAlpha=.7;ctx.strokeStyle='#d9ddbd';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(ox+8,oy-17);ctx.lineTo(W*.84,H*.4);ctx.lineTo(W*.91,H*.22);ctx.stroke();ctx.restore();
  ctx.fillStyle='rgba(192,208,195,.24)';ctx.font='12px monospace';ctx.textAlign='left';ctx.fillText('MILE MARKER 9',W*.07,H*.18);ctx.fillStyle='#d8ddcc';ctx.font='bold '+Math.max(18,Math.min(34,W*.04))+'px monospace';ctx.fillText('NO BACKUP ON SCENE',W*.07,H*.24);ctx.fillStyle='#abb7a6';ctx.font=Math.max(11,Math.min(16,W*.017))+'px monospace';ctx.fillText('One officer. No backup. Movement in the trees.',W*.07,H*.29);ctx.fillText('The radio is receiving a transmission from your own unit.',W*.07,H*.32);
  px(W*.07,H*.37,W*.005,H*.09,'#b34b43');ctx.fillStyle='#d4bb7e';ctx.font='bold 13px monospace';ctx.fillText('PRESS E / TAP SEARCH TO STEP OUT',W*.09,H*.415);drawVignette();
}
function drawVignette(){const v=ctx.createRadialGradient(W*.5,H*.48,Math.min(W,H)*.16,W*.5,H*.48,Math.max(W,H)*.8);v.addColorStop(0,'rgba(0,0,0,0)');v.addColorStop(.7,'rgba(0,0,0,.18)');v.addColorStop(1,'rgba(0,0,0,.72)');ctx.fillStyle=v;ctx.fillRect(0,0,W,H);}
function drawPrologue(){
  screenJitter();
  drawPrologueCall();
}
function drawPatrolCarWorld(){
  const x=245-camera.x+shakeX,y=278-camera.y+shakeY;
  if(x<-100||y<-100||x>W+100||y>H+100)return;
  ctx.save();ctx.translate(x,y);ctx.rotate(.78);
  px(-25,-44,50,88,'#070b08');px(-22,-40,44,80,'#a6aaa0');px(-18,-35,36,70,'#343b36');px(-17,-29,34,23,'#15221e');px(-17,7,34,20,'#15221e');px(-14,-4,28,12,'#202925');px(-21,-23,42,4,'#b4b5a4');px(-21,20,42,4,'#c2c0af');px(-19,-13,8,15,'#090d0b');px(11,-13,8,15,'#090d0b');px(-20,-38,10,5,'#d8c79c');px(10,-38,10,5,'#d8c79c');px(-19,34,9,5,'#ce433b');px(10,34,9,5,'#ce433b');px(-7,-6,14,12,'#111a16');px(-4,-2,8,4,'#c3b77d');px(-15,-2,11,5,Math.sin(state.elapsed*9)>0?'#d44a42':'#284b85');px(4,-2,11,5,Math.sin(state.elapsed*9)>0?'#284b85':'#d44a42');ctx.restore();
}

function worldCoordinates(screenX,screenY){
  return {x:screenX+camera.x,y:screenY+camera.y};
}
function nearestInteractable(){
  if(state.floor!=='outside')return nearestInteriorObject();
  const extraction=objects.find(o=>o.type==='exit');
  const rescuedCount=survivors.filter(s=>s.found||s.following||s.delivered).length;
  if(extraction&&rescuedCount>=2&&dist(player.x,player.y,extraction.x,extraction.y)<178)return extraction;
  let found=null;
  let best=Infinity;
  for(const o of objects){
    if(o.type==='exit')continue;
    if(o.missing)continue;
    if(o.type==='evidence'&&o.found)continue;
    if(o.type==='loot'&&o.found)continue;
    const d=dist(player.x,player.y,o.x,o.y);
    const reach=o.type==='building'?Math.max(98,Math.max(o.w,o.h)*.5+29):76;
    if(d<reach&&d<best){best=d;found=o;}
  }
  for(const s of survivors){
    if(s.delivered||s.found||s.following)continue;
    const d=dist(player.x,player.y,s.x,s.y);
    if(d<112&&d<best){best=d;found=s;}
  }
  if(extraction&&dist(player.x,player.y,extraction.x,extraction.y)<118)return extraction;
  return found;
}
function nearestInteriorObject(){
  if(!state.room)return null;
  let nearest=null;
  let best=88;
  for(const item of state.room.items){
    if((item.found&&item.type!=='intakeDesk')||item.missing)continue;
    const d=dist(player.x,player.y,item.x,item.y);
    if(d<best){best=d;nearest=item;}
  }
  const exit=state.room.exit;
  const exitDist=dist(player.x,player.y,exit.x,exit.y);
  if(exitDist<42&&exitDist<best)return {type:'exitRoom',name:'Exit building',x:exit.x,y:exit.y};
  return nearest;
}
function interact(){
  if(state.prologueStage==='call'){acceptDispatch();return;}
  if(state.prologueStage==='arrival'){enterNightSearch();return;}
  if(state.prologueStage==='drive'){toast('KEEP MOVING. MILE MARKER 9 IS AHEAD.',1.2);return;}
  if(!state.running||state.paused||state.gameOver||interactCooldown>0)return;
  interactCooldown=.15;
  audioStart();
  const target=nearestInteractable();
  if(!target){
    toast(state.floor==='outside'?'Nothing close enough to investigate.':'Nothing useful within reach.',1.2);
    return;
  }
  if(target.type==='evidence'||target.type==='note'){
    target.found=true;
    if(state.floor==='inside'&&target.id){state.roomItemStates=state.roomItemStates||{};state.roomItemStates[target.id]={found:true,missing:false};}
    evidence++;
    state.discovered++;
    addCaseRecord(target);
    state.noise=Math.max(state.noise,.2);
    state.intensity=Math.min(1,state.intensity+.12);
    sound('pickup');
    showRadioText(target.name,target.detail||'The evidence may be useful later.');
    toast('EVIDENCE BAGGED: '+target.name.toUpperCase()+'. OPEN CASE FILE [J] TO STUDY IT.',3.4);
    updateHUD();
    updateObjectives();
    activateMonster();
    if(evidence>=6&&!state.horrorEventFlags.sixthClueWhisper){state.horrorEventFlags.sixthClueWhisper=true;state.flashlightFlickerTimer=2.3;triggerWhisper('That was the last clue. I was hoping you would never find it.','center','VOICE INSIDE THE FILE');toast('THE SIXTH CLUE HAS YOUR HANDWRITING ON IT.',3.8);}
    return;
  }
  if(target.type==='memorial'){
    state.memorialTributeViewed=true;
    enterScreen('memorial');
    return;
  }
  if(target.type==='sideTask'){
    collectSideTask(target);
    return;
  }
  if(target.type==='witness'){
    beginWitnessInterview(target);
    return;
  }
  if(target.type==='intakeDesk'){
    openStationIntake();
    return;
  }
  if(target.type==='building'){
    enterBuilding(target);
    return;
  }
  if(target.type==='exitRoom'){
    leaveBuilding();
    return;
  }
  if(target.type==='loot'){
    collectLoot(target);
    return;
  }
  if(target.type==='exit'){
    tryExtraction();
    return;
  }
  if(target.following===false&&target.found===false&&typeof target.dialogue==='string'){
    target.found=true;
    target.following=true;
    state.noise=.15;
    sound('pickup');
    toast(target.name.toUpperCase()+': “'+target.dialogue+'”',4);
    updateHUD();
    updateObjectives();
    activateMonster();
    return;
  }
}
function collectSideTask(target){
  target.found=true;
  if(state.floor==='inside'&&target.id){state.roomItemStates=state.roomItemStates||{};state.roomItemStates[target.id]={found:true,missing:false};}
  if(target.task==='anchor'&&!state.anchorsDestroyed.includes(target.id)){
    state.anchorsDestroyed.push(target.id);
    state.noise=Math.max(state.noise,.6);
    state.intensity=1;
    state.flashlightFlickerTimer=Math.max(state.flashlightFlickerTimer||0,1.8);
    state.threatTier=Math.min(7,(state.threatTier||0)+1);
    caseRecords.push({id:'anchor-report-'+target.id,name:'Destroyed signal anchor: '+target.name,detail:target.detail,analysis:'This object was sustaining a signal that did not originate from any transmitter. Its removal has weakened the mimic network.',kind:'anomaly',studied:false});
    sound('scare');tone(44,.55,'sawtooth',.09,-28);
    toast('SIGNAL ANCHOR DESTROYED: '+state.anchorsDestroyed.length+'/3. SOMETHING HAS NOTICED.',3.3);
    if(state.anchorsDestroyed.length>=3&&!state.anchorsDisabled){
      state.anchorsDisabled=true;
      state.intensity=Math.max(.65,state.intensity);
      state.monsterSuppressedUntil=state.elapsed+45;
      caseRecords.push({id:'anchor-network-shutdown',name:'Signal network collapsed',detail:'All three anchors have been destroyed.',analysis:'The mimic network has weakened. The final extraction should be less crowded, and the recovered evidence may now support a true ending.',kind:'anomaly',studied:true});
      toast('OPTIONAL TASK COMPLETE: SIGNAL NETWORK DISABLED. TRUE ENDING AVAILABLE.',4.1);
    }
    updateObjectives();updateHUD();
  }
}
function collectLoot(target){
  target.found=true;
  if(state.floor==='inside'&&target.id){state.roomItemStates=state.roomItemStates||{};state.roomItemStates[target.id]={found:true,missing:false};}
  sound('pickup');
  if(target.loot==='ammo'){
    reserve+=12;
    toast('AMMUNITION SECURED: +12 ROUNDS.');
  }
  if(target.loot==='medkit'){
    medkits++;
    toast('FIRST-AID SUPPLIES ADDED TO YOUR KIT.');
  }
  if(target.loot==='battery'){
    batteryCells++;
    flashlightBattery=Math.min(100,flashlightBattery+22);
    toast('FLASHLIGHT BATTERIES RECOVERED.');
  }
  if(target.loot==='keys'){
    state.keysFound=true;
    toast('RELAY OVERRIDE KEY RECOVERED. THE BEACON WILL RESPOND WHEN THE CASE IS COMPLETE.');
  }
  updateHUD();
  updateInventory();
  updateObjectives();
}
function enterBuilding(target){
  if(state.floor!=='outside')return;
  state.lastBuildingExit={x:target.x,y:target.y+target.h/2+16};
  state.floor='inside';
  state.room=makeRoom(target.room);
  state.indoorPresence={timer:0,cooldown:6+Math.random()*4,x:clamp(player.x+choose([-1,1])*Math.min(280,state.room.w*.34),80,state.room.w-80),y:clamp(player.y-180,80,state.room.h-80),phase:Math.random()*9,arming:0,appearances:0};
  indoorEchoHistory=[];indoorEcho={active:false,timer:0,cooldown:8+Math.random()*5,x:0,y:0,angle:0,phase:Math.random()*9,roomId:target.room,roomAge:0};indoorEchoSampleTimer=.2;indoorEchoRoomId=target.room;
  if(target.room==='farmhouse'){state.indoorPresence.timer=1.2;state.indoorPresence.cooldown=8;state.intensity=1;state.screenShake=Math.max(state.screenShake,.28);voiceNoise(choose(['left','right']),.19);toast('THE UPSTAIRS FLOOR CREAKS. YOU ARE STILL ON THE GROUND FLOOR.',3.2);}
  player.x=state.room.spawn.x;
  player.y=state.room.spawn.y;
  player.angle=-Math.PI/2;
  player.speed=specs[state.selectedCharacter].speed*1.02;
  state.exploredRooms++;
  if(!state.exploredRoomIds.includes(target.room))state.exploredRoomIds.push(target.room);
  if(state.exploredRoomIds.length>=2&&!state.horrorEventFlags.secondStructureReveal){
    state.horrorEventFlags.secondStructureReveal=true;
    state.intensity=1;
    state.screenShake=Math.max(state.screenShake,.34);
    if(state.options.voiceWhispers)triggerWhisper('You are not the first person to enter this room tonight.','left','VOICE BEHIND THE DOOR');
    sound('scare');
    toast('THE DOOR CLOSES BEHIND YOU. THE ROOM WAS NOT LIKE THIS BEFORE.',4.2);
  }
  bullets=[];
  sound('door');
  toast('ENTERED: '+state.room.title+'. LISTEN BEFORE MOVING.',2.4);
  camera={x:0,y:0};
  updateHUD();
}
function leaveBuilding(){
  if(state.floor!=='inside'||!state.room)return;
  const exitName=state.room.title;
  state.floor='outside';
  state.room=null;
  player.speed=specs[state.selectedCharacter].speed;
  player.x=clamp(player.x+0,50,WORLD.w-50);
  player.y=clamp(player.y+0,50,WORLD.h-50);
  if(state.lastBuildingExit){
    player.x=state.lastBuildingExit.x;
    player.y=state.lastBuildingExit.y;
    state.lastBuildingExit=null;
  }else{
    if(exitName==='CHECKPOINT SHACK'){player.x=375;player.y=470;}
    if(exitName==='COUNTY POLICE STATION — INTAKE'||exitName==='COUNTY POLICE STATION'){player.x=930;player.y=815;}
    if(exitName==='SWAMP GAS STOP'){player.x=1480;player.y=545;}
    if(exitName==='LEANING CABIN'){player.x=1690;player.y=1380;}
    if(exitName==='RADIO RELAY HUT'){player.x=2390;player.y=1820;}
  }
  camera={x:clamp(player.x-W/2,0,WORLD.w-W),y:clamp(player.y-H/2,0,WORLD.h-H)};
  sound('door');
  toast('BACK OUTSIDE. THE RAIN HAS NOT STOPPED.',1.8);
  updateHUD();
}
function showRadioText(title,detail){
  $('radioText').innerHTML='<b>'+escapeHTML(title.toUpperCase())+'</b><br><br>'+escapeHTML(detail)+'<br><br><span style="color:#8b9a8b">EVIDENCE LOG UPDATED</span>';
  if(state.options.subtitles){
    state.radioTimer=7;
    state.radioLine=title+': '+detail;
  }
}
function escapeHTML(value){
  return String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}
function activateMonster(){
  if(monster.active)return;
  monster.active=true;
  monster.x=player.x+choose([-1,1])*650;
  monster.y=player.y+choose([-1,1])*500;
  monster.x=clamp(monster.x,100,WORLD.w-100);
  monster.y=clamp(monster.y,100,WORLD.h-100);
  monster.spotted=false;
  monster.hidden=false;
  monster.vanishTimer=0;
  monster.vanishCooldown=4.5+Math.random()*3.4;
  monster.activeTime=0;
  monster.reappearGlow=0;
  sound('scare');
  toast('THE RADIO CUTS OUT. SOMETHING IS MOVING THROUGH THE TREES.',3.3);
  state.screenShake=.4;
}
function spawnCrawlerWave(count=2,minRadius=180,speedBase=92,hp=2){
  if(state.floor!=='outside'||!player)return 0;
  if(state.anchorsDisabled&&state.extractionStarted)count=Math.max(1,count-1);
  let alive=crawlers.filter(c=>!c.dead).length;
  let made=0;
  for(let i=0;i<count&&alive<10;i++){
    const angle=(Math.PI*2*i/Math.max(1,count))+Math.random()*.55;
    const radius=minRadius+Math.random()*70;
    let x=clamp(player.x+Math.cos(angle)*radius,70,WORLD.w-70);
    let y=clamp(player.y+Math.sin(angle)*radius,70,WORLD.h-70);
    for(let attempt=0;attempt<5&&blockedAt(x,y,11);attempt++){
      const a=angle+attempt*1.17;
      x=clamp(player.x+Math.cos(a)*(radius+attempt*28),70,WORLD.w-70);
      y=clamp(player.y+Math.sin(a)*(radius+attempt*28),70,WORLD.h-70);
    }
    crawlers.push({x,y,r:11,hp:hp+Math.floor((state.threatTier||0)/3),speed:speedBase+(state.threatTier||0)*4+Math.random()*10,phase:Math.random()*8,alert:true,attack:0,dead:false,hiddenUntil:0});
    alive++;made++;
  }
  return made;
}
function updateThreatEscalation(dt){
  if(!state.running||state.paused||state.gameOver||state.prologueStage!=='swamp')return;
  const clues=collectedClueCount();
  const rescued=survivors.filter(s=>s.found||s.following||s.delivered).length;
  if(clues>=2&&!state.horrorEventFlags.pressureTwoClues){
    state.horrorEventFlags.pressureTwoClues=true;
    state.threatTier=Math.max(state.threatTier||0,1);
    state.intensity=Math.max(state.intensity,.62);
    state.apparitionCooldown=Math.min(state.apparitionCooldown,3.5);
    triggerWhisper('The second clue changes everything. It knows what you will open next.','left','CASE FILE // LIVE TRANSMISSION');
    toast('CASE PRESSURE INCREASED. YOUR EVIDENCE IS ATTRACTING SOMETHING.',3.4);
  }
  if(clues>=3&&!state.horrorEventFlags.pressureThreeClues){
    state.horrorEventFlags.pressureThreeClues=true;
    state.threatTier=Math.max(state.threatTier||0,2);
    state.flashlightFlickerTimer=1.5;
    state.screenShake=Math.max(state.screenShake,.25);
    spawnCrawlerWave(2,205,94,2);
    triggerWhisper('You have enough proof to leave. You do not have enough to survive leaving.','right','VOICE IN THE RECORDER');
    toast('THE TREELINE MOVED CLOSER WHILE YOU WERE READING.',3.2);
  }
  if(clues>=5&&!state.horrorEventFlags.pressureFiveClues){
    state.horrorEventFlags.pressureFiveClues=true;
    state.threatTier=Math.max(state.threatTier||0,3);
    state.flashlightFlickerTimer=2.1;
    state.intensity=1;
    if(state.floor==='outside')spawnCrawlerWave(2,230,103,3);
    triggerWhisper('Five pieces. Five versions of the same night. One of them is yours.','center','UNKNOWN CHANNEL');
    toast('THE EVIDENCE FILE NOW CONTAINS A PAGE WITH YOUR HANDWRITING.',3.8);
  }
  if(clues>=6&&!state.horrorEventFlags.pressureSixClues){
    state.horrorEventFlags.pressureSixClues=true;
    state.threatTier=Math.max(state.threatTier||0,4);
    state.flashlightFlickerTimer=Math.max(state.flashlightFlickerTimer||0,2.4);
    state.intensity=1;
    if(state.floor==='outside')spawnCrawlerWave(2,250,112,4);
    triggerWhisper('You found all six. Now the house knows you can prove it.','center','THE HOUSE IS ON THE CHANNEL');
    toast('THE CASE IS COMPLETE. THE NIGHT IS NOT.',4.1);
  }
  if(rescued>=1&&!state.horrorEventFlags.pressureFirstRescue){
    state.horrorEventFlags.pressureFirstRescue=true;
    state.threatTier=Math.max(state.threatTier||0,3);
    if(state.floor==='outside')spawnCrawlerWave(1,200,103,3);
    state.flashlightFlickerTimer=Math.max(state.flashlightFlickerTimer||0,1.1);
  }
  if(state.missingCount>=1&&!state.horrorEventFlags.pressureFirstDisappearance){
    state.horrorEventFlags.pressureFirstDisappearance=true;
    state.threatTier=Math.max(state.threatTier||0,3);
    state.flashlightFlickerTimer=Math.max(state.flashlightFlickerTimer||0,1.65);
    state.intensity=1;
    triggerWhisper('It has started taking the things you need. Next it will take the way back.','center','VOICE FROM THE EMPTY ROOM');
  }
  if(state.elapsed>=150&&!state.horrorEventFlags.pressureMidnight){
    state.horrorEventFlags.pressureMidnight=true;
    state.threatTier=Math.max(state.threatTier||0,4);
    if(state.floor==='outside')spawnCrawlerWave(2,240,110,3);
    state.flashlightFlickerTimer=Math.max(state.flashlightFlickerTimer||0,2.2);
    toast('THE NIGHT HAS CHANGED. THE THINGS OUT THERE HAVE STOPPED HIDING.',3.7);
    sound('roar');
  }
  if(state.elapsed>=270&&!state.horrorEventFlags.pressureLateNight){
    state.horrorEventFlags.pressureLateNight=true;
    state.threatTier=Math.max(state.threatTier||0,5);
    if(state.floor==='outside')spawnCrawlerWave(2,245,116,3);
    state.intensity=1;
    triggerWhisper('Dispatch is no longer on the other end. Something is waiting for you to finish the report.','left','CHANNEL ZERO');
  }
  state.flashlightFlickerTimer=Math.max(0,(state.flashlightFlickerTimer||0)-dt);
}

function studyCount(){
  return caseRecords.filter(r=>r.studied&&(r.kind==='evidence'||r.kind==='note')).length;
}
function collectedClueCount(){
  return caseRecords.filter(r=>r.kind==='evidence'||r.kind==='note').length;
}
function validCrossReferenceCount(){
  return state.caseComparisons.filter(report=>!String(report.id).startsWith('review-')&&!String(report.id).startsWith('general-')).length;
}
function investigationReady(){
  return collectedClueCount()>=6&&studyCount()>=6&&validCrossReferenceCount()>=4&&state.caseTheory==='mimic-timeline'&&state.witnessInterviewed&&state.witnessTrust>=2&&state.stationComplete;
}
function currentTasks(){
  const rescued=survivors.filter(s=>s.found||s.following||s.delivered).length;
  const collected=collectedClueCount();
  const studied=studyCount();
  return [
    {done:collected>=6,text:'INVESTIGATION: Recover at least six physical clues ('+Math.min(collected,6)+'/6).'},
    {done:studied>=6,text:'FORENSICS: Study six clues in the case file [J] ('+Math.min(studied,6)+'/6).'},
    {done:validCrossReferenceCount()>=4,text:'ANALYSIS: Produce four distinct cross-reference reports ('+validCrossReferenceCount()+'/4).'},
    {done:state.caseTheory==='mimic-timeline',text:'CASE THEORY: Explain the radio and timeline contradiction correctly.'},
    {done:state.witnessInterviewed&&state.witnessTrust>=2,text:state.witnessInterviewed&&state.witnessTrust<2?'WITNESS: Statement unreliable. Study six clues and interview Silas again.':'WITNESS: Obtain a corroborated statement from Silas Venn.'},
    {done:state.stationComplete,text:'POLICE STATION: Screen six visitors and correctly identify at least five. Current verified decisions: '+stationScore()+'/6.'},
    {done:rescued>=2,text:'RESCUE: Find both missing people ('+rescued+'/2).'},
    {done:state.won,text:'EXTRACTION: Leave with the survivors and a defensible case.'},
    {done:state.keysFound,text:'SUPPLY: Recover the relay override key inside the Radio Relay Hut.'},
    {done:state.exploredRoomIds.length>=5,text:'EXPLORATION: Search five different buildings ('+state.exploredRoomIds.length+'/5).'},
    {done:state.extractionHold>=30,text:'FINAL DEFENSE: Hold the extraction zone for 30 seconds.'},
    {done:state.anchorsDestroyed.length>=3,text:'OPTIONAL TRUE ENDING: Destroy the three signal anchors in the County Police Station, Pine Rest Motel, and St. Mercy Chapel ('+state.anchorsDestroyed.length+'/3).'},
    {done:state.helpCount>0,text:'SURVIVAL SUPPORT: Call your partner for a radio assist with H at least once.'},
    {done:state.huntsSurvived>=3,text:'NIGHTMARE CHALLENGE: Survive all three adaptive hunts ('+state.huntsSurvived+'/3).'}
  ];
}
function renderEvidenceBoard(){
  const board=$('evidenceBoard');
  if(!board)return;
  const records=caseRecords.slice().reverse();
  $('evidenceProgress').textContent=studyCount()+' clues studied · 6 required · '+collectedClueCount()+' physical clues collected · '+validCrossReferenceCount()+' distinct cross-reference reports · 4 required';
  board.innerHTML=records.length?records.map(r=>{
    const missing=r.kind==='absence';
    const status=missing?'DISAPPEARANCE REPORT':r.studied?'STUDIED · FINDINGS RECORDED':'UNEXAMINED EVIDENCE';
    const analysis=r.studied?'<p><b>FORENSIC FINDING</b><br>'+escapeHTML(r.analysis)+'</p>':'';
    const button=(!r.studied&&!missing)?'<button type="button" data-study-id="'+escapeHTML(r.id)+'">Study evidence</button>':missing?'':'<div class="evidence-meta">CROSS-REFERENCE SAVED</div>';
    return '<article class="evidence-card '+(r.studied?'studied':'')+(missing?' missing':'')+'"><div class="evidence-meta">'+status+'</div><h3>'+escapeHTML(r.name)+'</h3><p>'+escapeHTML(r.detail)+'</p>'+analysis+button+'</article>';
  }).join(''):'<div class="info-card">No physical evidence collected yet. Search glowing clues and readable notes, then return here to study them.</div>';
  const log=$('missingLog');
  if(log)log.innerHTML=state.disappearanceLog.length?state.disappearanceLog.slice().reverse().map(v=>'<div style="padding:6px 0;border-bottom:1px solid #263328"><b>'+escapeHTML(v.title)+'</b><br>'+escapeHTML(v.detail)+'</div>').join(''):'Nothing has gone missing yet. Keep track of the scene.';
  const report=$('comparisonReport');
  if(report&&state.caseComparisons.length)report.innerHTML=state.caseComparisons.slice().reverse().map(v=>'<div style="padding:8px 0;border-bottom:1px solid #263328"><b>'+escapeHTML(v.title)+'</b><br>'+escapeHTML(v.text)+'</div>').join('');
  for(const button of document.querySelectorAll('[data-theory]'))button.classList.toggle('selected',button.dataset.theory===state.pendingTheory);
  const theoryFeedback=$('theoryFeedback');
  if(theoryFeedback&&state.caseTheory==='mimic-timeline')theoryFeedback.innerHTML='<b>THEORY ACCEPTED · PROVISIONAL</b><br>The timeline supports an imitator using the dispatch channel. The witness statement and missing-item pattern must still be recorded before extraction.';
}
function selectCaseTheory(id){
  if(state.caseTheory==='mimic-timeline'){toast('CASE THEORY ALREADY ACCEPTED. Preserve the evidence and finish the interview.',2);return;}
  if(!['storm-failure','staged-witness','mimic-timeline','duplicate-units'].includes(id))return;
  state.pendingTheory=id;
  for(const button of document.querySelectorAll('[data-theory]'))button.classList.toggle('selected',button.dataset.theory===id);
  $('theoryFeedback').textContent='Selected working theory. Submit it when you are ready to defend your conclusion against the evidence.';
}
function submitCaseTheory(){
  if(!state.pendingTheory){toast('SELECT A CASE THEORY FIRST.',1.8);return;}
  if(collectedClueCount()<6){toast('THE THEORY IS NOT READY: RECOVER SIX PHYSICAL CLUES.',2.7);return;}
  if(studyCount()<6){toast('THE THEORY IS NOT READY: STUDY SIX PHYSICAL CLUES.',2.7);return;}
  if(validCrossReferenceCount()<4){toast('THE THEORY IS NOT READY: PRODUCE FOUR DISTINCT CROSS-REFERENCE REPORTS.',2.7);return;}
  state.theoryAttempts++;
  const hasLog=caseRecords.some(r=>r.id==='log'&&r.studied);
  const hasRadio=caseRecords.some(r=>r.id==='radio'&&r.studied);
  if(state.pendingTheory==='mimic-timeline'&&hasLog&&hasRadio){
    state.caseTheory='mimic-timeline';
    $('theoryFeedback').innerHTML='<b>THEORY ACCEPTED · PROVISIONAL</b><br>The dispatch log and radio recording show the same voice arriving before the call. Your best explanation is an imitator that can copy an officer and speak ahead of the event. You still need Silas’s signed statement and both survivors.';
    state.intensity=Math.min(1,state.intensity+.16);
    sound('radio');
    triggerWhisper('That is not what happened. That is what you can prove.','left','CASE FILE AUDIO');
    queueStoryScare('duplicate','caseTheoryAccepted',1.1);
    toast('CASE THEORY ACCEPTED. THE FILE HAS A NEW PAGE YOU DID NOT WRITE.',3.8);
  }else if(state.pendingTheory==='mimic-timeline'){
    state.caseTheory='';
    $('theoryFeedback').textContent='The explanation may fit, but the file cannot support it yet. Study both the waterlogged patrol log and cracked dispatch radio before submitting again.';
    toast('INSUFFICIENT SUPPORT: STUDY THE LOG AND RADIO RECORDING.',3.0);
  }else{
    state.caseTheory='';
    const feedback={
      'storm-failure':'REJECTED: weather can distort a signal, but it cannot explain the dispatch time written before the call or the voice repeating words that have not been spoken.',
      'staged-witness':'REJECTED: the witness may be unreliable, but the physical evidence predates your interview. A staged scene does not explain the impossible radio sequence.',
      'duplicate-units':'REJECTED: dispatch confirms one available unit. The duplicate signal uses your call sign but has no vehicle telemetry or second GPS trail.'
    };
    $('theoryFeedback').textContent=feedback[state.pendingTheory]||'Theory rejected. Review the evidence.';
    state.intensity=Math.min(1,state.intensity+.06);
    if(Math.random()<.5)triggerWhisper('Keep trying. You have time. You think.','right','VOICE IN THE FILE');
    toast('CASE THEORY REJECTED. THE EVIDENCE DOES NOT SUPPORT IT.',2.5);
  }
  updateObjectives();
  updateHUD();
}
function compareEvidence(){
  const studied=caseRecords.filter(r=>r.studied&&(r.kind==='evidence'||r.kind==='note'));
  if(studied.length<2){toast('CROSS-REFERENCE FAILED: STUDY TWO PHYSICAL CLUES FIRST.',2.5);return;}
  const ids=new Set(studied.map(r=>r.id));
  const names=new Set(studied.map(r=>r.name.toLowerCase()));
  const reports=[];
  if(ids.has('log')&&ids.has('radio'))reports.push({id:'log-radio',title:'DISPATCH TIMELINE CONTRADICTION',text:'The radio voice appears before the logged call. The timeline was not merely altered afterward; the recording suggests someone knew what dispatch would say before dispatch spoke.'});
  if(ids.has('cloth')&&ids.has('prints'))reports.push({id:'cloth-prints',title:'A SECOND SET OF MOVEMENTS',text:'The uniform fibers and the waterline prints do not describe the same person moving in one direction. Something may have returned from the water wearing a familiar uniform.'});
  if(ids.has('log')&&ids.has('badge'))reports.push({id:'log-badge',title:'UNIT 14 SHOULD NOT EXIST',text:'The scratched time and badge number refer to an officer absent from county assignment records. The official report may have been built around a nonexistent unit.'});
  if(ids.has('radio')&&ids.has('cloth'))reports.push({id:'radio-cloth',title:'THE VOICE WORE THE UNIFORM',text:'The voice on the radio uses the same phrase found in the uniform stitching pattern: an expression associated with a deputy who was never assigned to this unit.'});
  if(ids.has('radio')&&ids.has('badge'))reports.push({id:'radio-badge',title:'A CALL SIGN WITH NO OWNER',text:'The radio addresses the badge number of a deputy missing from assignment records. The signal appears to know the identity of the person it is trying to replace.'});
  if(ids.has('cloth')&&ids.has('badge'))reports.push({id:'cloth-badge',title:'THE UNIFORM DOES NOT FIT THE BADGE',text:'The recovered patch and badge belong to incompatible personnel records. The scene may contain pieces taken from more than one officer.'});
  if(ids.has('prints')&&ids.has('badge'))reports.push({id:'prints-badge',title:'THE RETURN TRACK',text:'The prints turn back from the water while the badge remains warm. Something returned to the bank after the missing deputy should have crossed away from it.'});
  if(names.has('final dispatch tape')&&ids.has('radio'))reports.push({id:'two-recordings',title:'THE VOICE PRECEDES THE EVENT',text:'Both recordings place a voice ahead of the event it describes. This is not a duplicate transmission; the sound is behaving like a rehearsal.'});
  if(!reports.length)reports.push({id:'general-'+state.caseComparisons.length,title:'PARTIAL PATTERN IDENTIFIED',text:'The studied items disagree on timing or origin. Their shared detail is that each was present before an event and altered or displaced afterward. Keep collecting evidence to isolate a reliable sequence.'});
  let added=0;
  for(const report of reports){
    if(state.caseComparisons.some(old=>old.id===report.id))continue;
    state.caseComparisons.push(report);
    added++;
  }
  if(!added){
    state.caseComparisons.push({id:'review-'+state.caseComparisons.length,title:'REVIEW CONFIRMED',text:'The previous contradiction still holds. No new report can be generated from this exact pair. Study another item and compare again.'});
  }
  const panel=$('comparisonReport');
  panel.innerHTML=state.caseComparisons.slice().reverse().map(v=>'<div style="padding:8px 0;border-bottom:1px solid #263328"><b>'+escapeHTML(v.title)+'</b><br>'+escapeHTML(v.text)+'</div>').join('');
  state.intensity=Math.min(1,state.intensity+.08);
  tone(310,.16,'triangle',.06,-120);
  toast('CROSS-REFERENCE COMPLETE: '+state.caseComparisons[state.caseComparisons.length-1].title,2.7);
  updateObjectives();
  updateHUD();
}
function addCaseRecord(target){
  const id=String(target.id||target.name||('clue-'+state.elapsed.toFixed(1)));
  if(caseRecords.some(r=>r.id===id))return;
  const analysis={
    log:'The log contains two dispatch times stamped only seconds apart. One entry was recorded before Unit 14 left the station. The handwriting on the second timestamp is identical, but the ink is on top of the water damage.',
    radio:'Two voices occupy the same channel at once. The lower voice repeats the officer’s words a fraction of a second before they are spoken. This is not ordinary radio echo.',
    cloth:'The patch carries fresh marsh silt and a pale thread not used on state uniforms. The stitching is pulled outward, as if the uniform was taken off someone who was moving away.',
    prints:'The large prints stop at the waterline. Smaller prints appear on the far side, facing back toward the bank. The pattern suggests something crossed the water and returned wearing a different gait.',
    badge:'The badge is still warmer than the surrounding air. The last four digits match the number scratched into the patrol log, but the badge number itself belongs to a deputy officially listed as never assigned to this county.',
    'incident memo':'The memo is signed by a supervisor who retired eleven years before this checkpoint was built. The ink is fresh.',
    'missing person report':'The hikers were reported missing before the emergency call was placed. Their recorded last location changes every time the report is copied.',
    'generator log':'The final generator entry is written in a hand that matches the scratched dispatch timestamp. The log reports power loss before the generator was switched on.',
    'receipt with a warning':'The receipt is time-stamped tomorrow. It lists one item: a replacement radio for a unit that does not exist.',
    'handwritten warning':'The writing pressure cuts through several pages below this one. The same sentence appears in reverse on the last sheet.',
    'final dispatch tape':'The tape contains the officer’s next sentence before it is spoken. A second breath continues for several seconds after the tape ends.'
  };
  const key=String(target.id||target.name||'').toLowerCase();
  let finding=analysis[key];
  if(!finding){
    const name=String(target.name||'').toLowerCase();
    finding=analysis[name]||('The object has been logged and photographed. Its details do not match the official timeline. Compare its time, material, and location with another clue before deciding what it proves.');
  }
  caseRecords.push({id,name:target.name||'Unidentified clue',detail:target.detail||'Recovered from the incident scene.',analysis:finding,kind:target.type==='note'?'note':'evidence',studied:false});
}
function studyEvidence(id){
  const record=caseRecords.find(r=>r.id===id);
  if(!record||record.studied)return;
  record.studied=true;
  state.noise=Math.max(state.noise,.1);
  state.intensity=Math.min(1,state.intensity+.09);
  tone(520,.09,'triangle',.07,-90);
  if(studyCount()===2){
    record.analysis+=' Cross-reference: another clue suggests the missing officer’s last known position was deliberately changed in the records.';
  }
  toast('FORENSIC REVIEW COMPLETE: '+record.name.toUpperCase(),2.6);
  updateObjectives();
  updateHUD();
}
function updateObjectives(){
  const tasks=currentTasks();
  $('taskList').innerHTML=tasks.map(t=>'<div class="task-row '+(t.done?'done':'')+'"><div class="task-mark">'+(t.done?'✓':'□')+'</div><div class="task-copy">'+escapeHTML(t.text)+'</div></div>').join('');
  renderEvidenceBoard();
}
function updateSurvivorLocator(){
  const box=$('survivorLocator');
  const main=$('survivorLocatorMain');
  const sub=$('survivorLocatorSub');
  if(!box||!main||!sub)return;
  if(!state.running||state.prologueStage!=='swamp'||state.gameOver){box.classList.remove('visible');return;}
  const navTarget=state.floor==='outside'?currentOutdoorTarget():null;
  if(navTarget&&navTarget.navKind!=='survivor'&&navTarget.navKind!=='exit'){
    box.classList.remove('visible');
    return;
  }
  box.classList.add('visible');
  if(state.floor==='inside'){
    main.textContent='SURVIVOR SIGNAL: OUTSIDE';
    sub.textContent='Exit this building, then follow the green signal arrow.';
    return;
  }
  const missing=survivors.filter(s=>!s.found&&!s.following&&!s.delivered).sort((a,b)=>dist(player.x,player.y,a.x,a.y)-dist(player.x,player.y,b.x,b.y));
  const rescued=survivors.filter(s=>s.found||s.following||s.delivered).length;
  const followers=survivors.filter(s=>s.following&&!s.delivered);
  if(missing.length){
    const target=missing[0];
    const d=dist(player.x,player.y,target.x,target.y);
    const a=angleTo(player.x,player.y,target.x,target.y);
    const arrows=['→','↘','↓','↙','←','↖','↑','↗'];
    const direction=arrows[(Math.round(a/(Math.PI/4)+8)%8)];
    main.innerHTML=escapeHTML(target.name.toUpperCase())+' <span class="locator-range">'+direction+' '+Math.round(d)+'m</span>';
    const phrase=d<150?'YOU ARE CLOSE — PRESS E / SEARCH TO RESCUE.':d<420?'SIGNAL STRONG — FOLLOW THE GREEN BEACON.':'SIGNAL WEAK — FOLLOW THE EDGE ARROW AND GREEN MINIMAP MARKER.';
    sub.textContent='RESCUED: '+rescued+'/2 · '+phrase;
    return;
  }
  if(rescued>=2&&!investigationReady()){
    main.textContent='SURVIVORS SECURED · CASE INCOMPLETE';
    sub.textContent='Recover and study six clues, produce four distinct cross-reference reports, screen six visitors at the County Police Station (five correct), recover the relay key, search five buildings, save Silas’s statement, and survive extraction.';
    return;
  }
  if(rescued>=2&&(!state.keysFound||state.exploredRoomIds.length<5)){
    main.textContent='CASEWORK DONE · PREPARE EXTRACTION';
    sub.textContent=(!state.keysFound?'Recover the relay override key in the Radio Relay Hut. ':'')+(state.exploredRoomIds.length<5?'Search '+(5-state.exploredRoomIds.length)+' more different building(s).':'')+' Then follow the gold beacon and hold for 30 seconds.';
    return;
  }
  if(rescued>=2){
    const exit=objects.find(o=>o.type==='exit');
    const d=exit?dist(player.x,player.y,exit.x,exit.y):0;
    const a=exit?angleTo(player.x,player.y,exit.x,exit.y):0;
    const arrows=['→','↘','↓','↙','←','↖','↑','↗'];
    const direction=arrows[(Math.round(a/(Math.PI/4)+8)%8)];
    main.innerHTML=state.extractionStarted?'DEFEND EXTRACTION <span class="locator-range">'+Math.max(0,30-Math.floor(state.extractionHold))+'s</span>':'CASE READY <span class="locator-range">'+direction+' '+Math.round(d)+'m</span>';
    sub.textContent=state.extractionStarted?'EXTRACTION UNDER ATTACK · HOLD POSITION. LEAVING RESETS THE TIMER.':'Casework complete. Press E at the gold beacon and survive the 30-second defense.';
    return;
  }
  main.textContent='SEARCH FOR SURVIVORS';
  sub.textContent='Follow the pulsing green markers and use E when close.';
}
function updateHUD(){
  if(!player)return;
  $('health').textContent=player.hp>70?'CONDITION: STABLE':player.hp>35?'CONDITION: WOUNDED':'CONDITION: CRITICAL';
  $('healthfill').style.width=clamp(player.hp/player.maxHp*100,0,100)+'%';
  $('staminafill').style.width=clamp(stamina/player.maxStamina*100,0,100)+'%';
  $('ammo').textContent=ammo;
  $('reserve').textContent=reserve;
  $('evidence').textContent=Math.min(collectedClueCount(),6)+'/6';
  const rescuedCount=survivors.filter(s=>s.found||s.following||s.delivered).length;
  $('survivors').textContent=rescuedCount+'/2';
  $('battery').textContent=Math.floor(flashlightBattery)+'%';
  $('officerName').textContent=specs[state.selectedCharacter].name.replace(/^Officer\s+/i,'').toUpperCase();
  const minutes=Math.floor(state.missionClock/60);
  const seconds=Math.floor(state.missionClock%60);
  $('timeReadout').textContent=String(2+Math.floor(minutes/60)).padStart(2,'0')+':'+String(minutes%60).padStart(2,'0')+' AM';
  $('status').textContent=monster&&monster.active?(monster.hidden?'RADIO: VISUAL CONTACT LOST':'RADIO: SIGNAL LOST'):'RADIO: DISPATCH STANDBY';
  const completeSurvivors=survivors?survivors.filter(s=>s.found||s.following||s.delivered).length:0;
  if(state.extractionStarted){$('objective').textContent='EXTRACTION DEFENSE: HOLD THE BEACON '+Math.min(30,Math.floor(state.extractionHold))+'/30 SECONDS. DO NOT LEAVE THE ZONE.';}
  else if(collectedClueCount()<6){$('objective').textContent='INVESTIGATE: Collect six clues ('+Math.min(collectedClueCount(),6)+'/6), then study them with J.';}
  else if(studyCount()<6){$('objective').textContent='FORENSICS: Study six clues in your case file ['+studyCount()+'/6]. Press J.';}
  else if(validCrossReferenceCount()<4){$('objective').textContent='ANALYSIS: Produce four DISTINCT cross-reference reports in your case file ['+validCrossReferenceCount()+'/4].';}
  else if(state.caseTheory!=='mimic-timeline'){$('objective').textContent='CASE THEORY: Submit a supported explanation in your case file [J].';}
  else if(!state.witnessInterviewed){$('objective').textContent='WITNESS: Interview Silas Venn inside Cypress Farmhouse.';}
  else if(state.witnessTrust<2){$('objective').textContent='WITNESS: Silas’s statement is unreliable. Study six clues, return to him, and earn a corroborated statement.';}
  else if(!state.stationComplete){$('objective').textContent='INTAKE: Screen six visitors inside the County Police Station. Verify IDs and the duty roster.';}
  else if(!state.keysFound){$('objective').textContent='SUPPLY: Recover the relay override key inside the Radio Relay Hut.';}
  else if(state.exploredRoomIds.length<5){$('objective').textContent='EXPLORATION: Search five different buildings ['+state.exploredRoomIds.length+'/5].';}
  else if(completeSurvivors<2){$('objective').textContent='RESCUE: Find the missing people '+completeSurvivors+'/2. Follow green markers.';}
  else{$('objective').textContent='CASE READY: Press E at the gold beacon and survive the 30-second defense.';}
  updateSurvivorLocator();
  const near=player&&state.running&&!state.hideSpotActive?nearestInteractable():null;
  if(state.hideSpotActive){
    $('prompt').textContent='HIDDEN IN '+state.hideSpotName.toUpperCase()+' · C EMERGE';
    $('interactNotice').textContent='LISTEN. DO NOT MOVE OR THE CREATURE WILL HEAR YOU.';
  }else if(near){
    $('prompt').textContent='E / SEARCH — '+String(near.name||'Investigate').toUpperCase();
    $('interactNotice').textContent='[ E ]  '+String(near.name||'INVESTIGATE').toUpperCase();
  }else{
    $('prompt').textContent='WASD MOVE · SHIFT SPRINT · E SEARCH · F LIGHT · C HIDE · G SCREAM · H HELP · J CASE FILE';
    $('interactNotice').textContent='';
  }
}
function updateInventory(){
  $('inventorySummary').innerHTML='<b>'+escapeHTML(specs[state.selectedCharacter].name.toUpperCase())+'</b><br>Health: '+Math.ceil(player.hp)+' / '+player.maxHp+'<br>Stamina: '+Math.ceil(stamina)+' / '+player.maxStamina+'<br>Loaded magazine: '+ammo+' rounds<br>Spare ammunition: '+reserve+' rounds<br>Flashlight: '+Math.floor(flashlightBattery)+'%';
  $('invAmmo').textContent=reserve;
  $('invMed').textContent=medkits;
  $('invBat').textContent=batteryCells;
  $('invKeys').textContent=state.keysFound?'Found':'Missing';
  $('useMed').disabled=medkits<=0||player.hp>=player.maxHp;
}
function findHidingSpot(){
  if(state.floor==='inside'&&state.room){
    let found=null,best=Infinity;
    const allowed=new Set(['cabinet','bed','table','shelves','desk']);
    for(const p of state.room.props){
      if(!allowed.has(p.t))continue;
      const edgeX=Math.max(0,Math.abs(player.x-p.x)-p.w/2);
      const edgeY=Math.max(0,Math.abs(player.y-p.y)-p.h/2);
      const d=Math.hypot(edgeX,edgeY);
      if(d<42&&d<best){best=d;found={name:p.t==='cabinet'?'inside the cabinet':p.t==='bed'?'under the bed':p.t==='table'?'under the table':p.t==='shelves'?'behind the shelves':'behind the desk',id:state.room.id+'-'+p.t+'-'+Math.round(p.x)+'-'+Math.round(p.y)};}
    }
    return found;
  }
  if(state.floor==='outside'){
    let best=null,bestD=110;
    for(const t of trees){
      const d=dist(player.x,player.y,t.x,t.y);
      if(d<bestD&&d>17){bestD=d;best={name:'the tree line',id:'tree-'+Math.round(t.x)+'-'+Math.round(t.y)};}
    }
    if(best)return best;
    if(treeNear(player.x,player.y,100,100))return {name:'the reeds',id:'reeds'};
  }
  return null;
}
function toggleHide(){
  if(!state.running||state.paused||state.gameOver||state.screen!=='game')return;
  if(state.hideSpotActive){
    state.hideSpotActive=false;player.hidden=false;state.hideElapsed=0;state.hideRisk=0;state.hideSpotName='';state.noise=Math.max(state.noise,.22);if(state.hideRestoreFlashlight&&flashlightBattery>0)flashlight=true;state.hideRestoreFlashlight=false;sound('door');toast('YOU LEAVE COVER. THE FLOOR CREAKS UNDER YOUR WEIGHT.',2.1);updateHUD();return;
  }
  const spot=findHidingSpot();
  if(!spot){toast(state.floor==='inside'?'NO COVER HERE. TRY A CABINET, BED, TABLE, OR SHELVES.':'FIND A TREE OR REEDS AND GET CLOSE BEFORE HIDING.',2.2);return;}
  state.hideRestoreFlashlight=flashlight;
  if(flashlight)flashlight=false;
  state.adaptiveHorror.hideCount=Math.min(20,(state.adaptiveHorror.hideCount||0)+1);state.hideSpotActive=true;state.hideSpotName=spot.name;state.hideElapsed=0;state.hideRisk=0;player.hidden=true;player.moving=false;state.noise=Math.min(state.noise,.06);sound('door');tone(92,.12,'triangle',.04,-35);toast('HIDING '+spot.name.toUpperCase()+'. THE FLASHLIGHT GOES DARK. STAY STILL. C TO EMERGE.',2.8);updateHUD();
}
function playerScream(){
  if(!state.running||state.paused||state.gameOver||state.screen!=='game')return;
  if(state.screamCooldown>0){toast('YOUR THROAT IS RAW. SCREAM READY IN '+Math.ceil(state.screamCooldown)+'s.',1.6);return;}
  state.screamCooldown=16;
  state.screamPulseTimer=.72;
  state.screamPulseRadius=0;
  state.shoutCount=(state.shoutCount||0)+1;
  state.noise=1;
  state.intensity=1;
  state.hideSpotActive=false;state.hideElapsed=0;state.hideRisk=0;state.hideSpotName='';player.hidden=false;if(state.hideRestoreFlashlight&&flashlightBattery>0)flashlight=true;state.hideRestoreFlashlight=false;
  sound('scare');tone(58,.75,'sawtooth',.14,-20);tone(173,.42,'square',.055,61);
  let staggered=0;
  for(const c of crawlers){
    if(c.dead)continue;
    const d=dist(player.x,player.y,c.x,c.y);
    if(d<255){c.stunned=Math.max(c.stunned||0,2.4);c.alert=true;staggered++;}
  }
  if(monster&&monster.active){
    const d=dist(player.x,player.y,monster.x,monster.y);
    if(!monster.hidden&&d<330)monster.stun=Math.max(monster.stun,.85);
    monster.vanishCooldown=Math.min(monster.vanishCooldown||10,2.5);
  }else activateMonster();
  toast(staggered?'YOU SCREAMED. '+staggered+' CREATURE(S) STAGGER. SOMETHING ELSE HEARD YOU.':'YOUR SCREAM VANISHES INTO THE TREES. SOMETHING ANSWERS FROM FAR TOO CLOSE.',3.1);
  if(state.options.voiceWhispers&&Math.random()<.7)triggerWhisper(choose(['Do it again. I want to know where you are.','That was not your voice at the end.','Your partner heard the scream before you opened your mouth.','I can scream louder.']),choose(['left','right']),'ECHO RESPONSE');
  updateHUD();
}
function callPartnerForHelp(){
  if(!state.running||state.paused||state.gameOver||state.screen!=='game')return;
  if(state.helpCooldown>0){toast('RADIO SUPPORT UNAVAILABLE FOR '+Math.ceil(state.helpCooldown)+'s.',1.6);return;}
  state.helpCooldown=38;state.helpTimer=5;state.helpCount++;
  addPartnerMessage('I NEED HELP. MARK MY POSITION.','outgoing');
  addPartnerMessage('I have your beacon. I can only send a short signal pulse, not a physical unit. Watch the marked movement and get to cover.','incoming');
  flashlightBattery=Math.min(100,flashlightBattery+13);
  for(const c of crawlers){if(!c.dead&&dist(player.x,player.y,c.x,c.y)<340)c.stunned=Math.max(c.stunned||0,1.8);}
  if(state.floor==='inside'&&state.indoorPresence&&state.indoorPresence.timer>0)state.indoorPresence.timer=Math.min(state.indoorPresence.timer,.7);
  state.noise=Math.max(state.noise,.76);
  sound('radio');tone(440,.14,'sine',.06,-90);tone(320,.19,'sine',.04,-90);
  toast('PARTNER SIGNAL PULSE: BATTERY +13%. NEARBY THREATS MOMENTARILY MARKED. RADIO NOISE MAY ATTRACT THE SMILER.',3.2);
  updateHUD();updateInventory();
}
function drawScreamPulse(){
  if(state.screamPulseTimer<=0||!player)return;
  const progress=1-state.screamPulseTimer/.72;
  const radius=18+progress*260;
  const x=player.x-camera.x+shakeX,y=player.y-camera.y+shakeY;
  ctx.save();ctx.globalAlpha=1-progress;ctx.strokeStyle='#c84a4b';ctx.lineWidth=3-progress*1.5;ctx.shadowColor='#a91d2a';ctx.shadowBlur=18;
  ctx.beginPath();ctx.arc(x,y,radius,0,Math.PI*2);ctx.stroke();ctx.shadowBlur=0;
  ctx.strokeStyle='rgba(223,194,168,'+(.55*(1-progress))+')';ctx.lineWidth=1;ctx.beginPath();ctx.arc(x,y,radius*.78,0,Math.PI*2);ctx.stroke();ctx.restore();
}
function updateSurvivalActions(dt){
  state.screamCooldown=Math.max(0,state.screamCooldown-dt);
  state.helpCooldown=Math.max(0,state.helpCooldown-dt);
  state.helpTimer=Math.max(0,state.helpTimer-dt);
  state.screamPulseTimer=Math.max(0,state.screamPulseTimer-dt);
  if(state.screamPulseTimer>0)state.screamPulseRadius=(1-state.screamPulseTimer/.72)*260;
  if(state.hideSpotActive){
    state.hideElapsed+=dt;
    const activeThreat=state.hideSpotActive&&monster&&monster.active&&!monster.hidden&&dist(player.x,player.y,monster.x,monster.y)<150;
    if(activeThreat)state.hideRisk+=dt*(state.noise>.3?1.35:state.huntActive?1.02:.72);else state.hideRisk=Math.max(0,state.hideRisk-(state.huntActive?.12:.35)*dt);
    if(state.huntActive&&state.hideElapsed>2.5&&monster&&monster.active&&!monster.hidden&&dist(player.x,player.y,monster.x,monster.y)<260)state.hideRisk+=dt*.3;
    state.noise=Math.max(0,state.noise-dt*.75);
    if(state.hideElapsed>13.5){state.hideSpotActive=false;player.hidden=false;state.hideSpotName='';state.hideElapsed=0;state.hideRisk=0;state.noise=Math.max(state.noise,.38);if(state.hideRestoreFlashlight&&flashlightBattery>0)flashlight=true;state.hideRestoreFlashlight=false;toast('YOUR BREATH RUNS OUT. YOU HAVE TO MOVE.',2.5);}
    else if(state.hideRisk>3.2){state.hideSpotActive=false;player.hidden=false;state.hideSpotName='';state.hideElapsed=0;state.hideRisk=0;state.noise=.8;state.intensity=1;state.screenShake=Math.max(state.screenShake,.28);if(state.hideRestoreFlashlight&&flashlightBattery>0)flashlight=true;state.hideRestoreFlashlight=false;toast('THE SMILER FOUND YOUR HIDING PLACE.',2.9);damagePlayer(18,'smiler');}
  }
  const moving=keys.w||keys.a||keys.s||keys.d||keys.arrowup||keys.arrowdown||keys.arrowleft||keys.arrowright;
  if(state.hideSpotActive&&moving){state.hideSpotActive=false;player.hidden=false;state.hideSpotName='';state.hideElapsed=0;state.hideRisk=0;state.noise=Math.max(state.noise,.35);if(state.hideRestoreFlashlight&&flashlightBattery>0)flashlight=true;state.hideRestoreFlashlight=false;toast('YOU SCRAMBLE OUT OF COVER. IT HEARD YOU.',1.9);}
  const hideBtn=$('hideAction'),screamBtn=$('screamAction'),helpBtn=$('helpAction'),status=$('survivalStatus');
  if(hideBtn){hideBtn.textContent=state.hideSpotActive?'C · EMERGE':'C · HIDE';hideBtn.setAttribute('aria-label',state.hideSpotActive?'Leave hiding place':'Hide in nearby cover');}
  if(screamBtn){screamBtn.disabled=state.screamCooldown>0;screamBtn.textContent=state.screamCooldown>0?'G · SCREAM '+Math.ceil(state.screamCooldown)+'s':'G · SCREAM';}
  if(helpBtn){helpBtn.disabled=state.helpCooldown>0;helpBtn.textContent=state.helpCooldown>0?'H · HELP '+Math.ceil(state.helpCooldown)+'s':'H · HELP';}
  if(status){
    if(state.hideSpotActive)status.textContent='HIDDEN '+Math.min(100,Math.floor(state.hideElapsed/13.5*100))+'% · STAY STILL';
    else if(state.helpTimer>0)status.textContent='RADIO PULSE ACTIVE · '+Math.ceil(state.helpTimer)+'s';
    else status.textContent='RUN · HIDE · SCREAM · CALL FOR HELP';
  }
}

function useMedkit(){
  if(medkits<=0){toast('NO MEDICAL PACKS LEFT.');return;}
  if(player.hp>=player.maxHp){toast('YOU ARE ALREADY IN GOOD CONDITION.');return;}
  medkits--;
  player.hp=Math.min(player.maxHp,player.hp+42);
  health=player.hp;
  sound('pickup');
  toast('FIELD DRESSING APPLIED. HEALTH RESTORED.');
  updateHUD();
  updateInventory();
}
function tryExtraction(){
  const rescued=survivors.filter(s=>s.found||s.following||s.delivered).length;
  if(rescued<2){
    toast('EXTRACTION LOCKED: RESCUE BOTH MISSING PEOPLE ('+rescued+'/2).',3.2);
    state.exitHintCooldown=4;
    return;
  }
  if(collectedClueCount()<6){
    toast('EXTRACTION LOCKED: COLLECT SIX PHYSICAL CLUES ('+collectedClueCount()+'/6).',3.5);
    state.exitHintCooldown=4;
    return;
  }
  if(studyCount()<6){
    toast('EXTRACTION LOCKED: STUDY SIX CLUES IN YOUR CASE FILE [J] ('+studyCount()+'/6).',3.5);
    state.exitHintCooldown=4;
    return;
  }
  if(validCrossReferenceCount()<4){
    toast('EXTRACTION LOCKED: PRODUCE FOUR DISTINCT CROSS-REFERENCE REPORTS ('+validCrossReferenceCount()+'/4).',3.5);
    state.exitHintCooldown=4;
    return;
  }
  if(state.caseTheory!=='mimic-timeline'){
    toast('EXTRACTION LOCKED: SUBMIT A SUPPORTED CASE THEORY IN YOUR CASE FILE [J].',3.5);
    state.exitHintCooldown=4;
    return;
  }
  if(!state.witnessInterviewed){
    toast('EXTRACTION LOCKED: INTERVIEW SILAS VENN INSIDE CYPRESS FARMHOUSE.',3.5);
    state.exitHintCooldown=4;
    return;
  }
  if(state.witnessTrust<2){
    toast('EXTRACTION LOCKED: SILAS’S STATEMENT IS NOT CORROBORATED. STUDY SIX CLUES AND INTERVIEW HIM AGAIN.',4.0);
    state.exitHintCooldown=4;
    return;
  }
  if(!state.keysFound){
    toast('EXTRACTION LOCKED: RECOVER THE RELAY OVERRIDE KEY IN THE RADIO RELAY HUT.',3.5);
    state.exitHintCooldown=4;
    return;
  }
  if(state.exploredRoomIds.length<5){
    toast('EXTRACTION LOCKED: SEARCH FIVE DIFFERENT BUILDINGS ('+state.exploredRoomIds.length+'/5).',3.5);
    state.exitHintCooldown=4;
    return;
  }
  if(!investigationReady()){
    toast('EXTRACTION LOCKED: FINISH THE FULL EVIDENCE REVIEW.',3.5);
    state.exitHintCooldown=4;
    return;
  }
  if(state.extractionStarted){
    toast('EXTRACTION ALREADY ACTIVE. HOLD THE ZONE UNTIL THE 30-SECOND TIMER ENDS.',2.2);
    return;
  }
  state.extractionStarted=true;
  state.extractionHold=0;
  state.extractionWave1=false;
  state.extractionWave2=false;
  state.extractionWave3=false;
  state.extractionWave4=false;
  state.extractionLastToast=0;
  state.extractionWasOutside=false;
  state.intensity=1;
  state.noise=1;
  sound('scare');
  tone(48,1.2,'sawtooth',.18,-20);
  toast('EXTRACTION UNDER ATTACK. HOLD THE BEACON FOR 30 SECONDS. FOUR WAVES ARE COMING. LEAVING RESETS THE TIMER.',5.2);
}
function completeExtraction(){
  for(const survivor of survivors){
    if(survivor.found||survivor.following||survivor.delivered){
      survivor.found=true;
      survivor.following=false;
      survivor.delivered=true;
      survivor.x=2920+(survivor.id==='ana'?-22:22);
      survivor.y=2300+18;
    }
  }
  state.rescued=survivors.filter(s=>s.delivered).length;
  state.won=true;
  updateObjectives();
  updateHUD();
  finishGame(true);
}
function finishGame(success){
  state.gameOver=true;
  state.running=false;
  state.won=success;
  state.screen='ending';
  $('hud').style.display='none';
  document.body.classList.remove('game-active');
  state.trueEnding=!!(success&&state.anchorsDisabled);
  $('endingTitle').textContent=!success?'OFFICER LOST IN THE MARSH':state.trueEnding?'TRUE ENDING // SIGNAL SILENCED':'INCIDENT CLOSED // SIGNAL STILL ACTIVE';
  $('endingText').textContent=!success?'Your radio keeps transmitting after your pulse stops. The rescue team finds the flashlight still on. Your footprints end inside a locked room. On the recovered tape, someone inside the room asks the team to let you out. They are using your voice, but the last word is spoken before the question begins.':state.trueEnding?'You got both survivors out and destroyed all three signal anchors. The final transmission stops in the middle of a syllable. For the first time all night, the radio is silent. At the debrief, the bodycam shows a third survivor standing behind you. Their face is yours, but they do not follow the others out. The signal is weaker now. It is not gone.':'You got both survivors out. During debrief, dispatch confirms that three people reached the perimeter. Your bodycam recorded four. The station has been sealed for eleven years, but Camera 04 logged you behind the intake glass at 02:17 tomorrow. Your partner sends one final message: “I am still outside. Who did we bring home?” The message is timestamped six minutes before you began the patrol.';
  $('radioBreachPanel').classList.add('hidden');state.radioIncidentActive=false;state.radioIncidentTimer=0;state.paused=false;$('huntBanner').classList.remove('active');$('realityPulse').classList.remove('active');document.body.classList.remove('hunting');
  $('endingStats').innerHTML='TIME IN FIELD: '+Math.floor(state.elapsed/60)+' MINUTES<br>HUNTS SURVIVED: '+state.huntsSurvived+'/3<br>SIGNAL ANCHORS DESTROYED: '+state.anchorsDestroyed.length+'/3<br>RADIO HELP CALLS: '+state.helpCount+'<br>SCREAMS: '+(state.shoutCount||0)+'<br>EVIDENCE RECOVERED: '+collectedClueCount()+'<br>CLUES STUDIED: '+studyCount()+'<br>CROSS-REFERENCES: '+validCrossReferenceCount()+'<br>RELAY KEY: '+(state.keysFound?'RECOVERED':'MISSING')+'<br>WITNESS STATEMENT: '+(state.witnessInterviewed?(state.witnessTrust>=2?'CORROBORATED':'UNRELIABLE'):'MISSING')+'<br>SURVIVORS EXTRACTED: '+survivors.filter(s=>s.delivered).length+'/2<br>CRAWLERS NEUTRALIZED: '+state.kills+'<br>SHOTS FIRED: '+state.shots+'<br>BUILDINGS SEARCHED: '+state.exploredRoomIds.length+'<br>EXTRACTION HOLD: '+Math.floor(state.extractionHold)+'/30 SECONDS';
  setScreen('ending');
  if(success)tone(460,.4,'sine',.1,180);else sound('scare');
  if(cloudAccount)cloudSubmitRun(success);
}
function enterScreen(name){
  if(!state.running)return;
  state.running=false;
  state.paused=true;
  setScreen(name);
}
function closeOverlay(){
  state.paused=false;
  state.running=true;
  state.screen='game';
  for(const id of ['objectivePanel','inventoryPanel','pausePanel','radioPanel','interviewPanel','stationIntakePanel','suspectZoomPanel','memorialPanel'])$(id).classList.add('hidden');
  $('hud').style.display='block';
  document.body.classList.add('game-active');
  state.lastFrame=performance.now();
  requestAnimationFrame(loop);
}
function pauseGame(){
  if(!state.running||state.gameOver)return;
  state.paused=true;
  state.running=false;
  setScreen('pause');
}
function openObjectives(){
  if(!state.running)return;
  updateObjectives();
  enterScreen('objectives');
}
const stationSuspects=[
  {name:'Aaron Pike',role:'County Deputy · Unit 06',badge:'FSP-0614',truth:'admit',intro:'The visitor holds out both hands before you ask. “I am Deputy Aaron Pike. North culvert assignment. I heard the dispatch call twice.” His uniform is soaked, but the floor under him stays dry.',identity:'The county seal, photograph, fingerprint prompt, and serial FSP-0614 match the personnel card. The hologram moves normally under the lamp.',purpose:'“Unit 06 was sent to the north culvert at 21:40. I called in from the shoulder. Someone answered in my own voice, half a second before I keyed the mic.”',records:'The duty roster confirms Aaron Pike, Unit 06, checked out at 21:40. The serial is valid. His unit has been marked MISSING since 02:17, but his identity is genuine.',openReply:'He glances at the observation window. “If there is somebody behind you, do not ask them to show their badge.”'},
  {name:'Lena Ward',role:'Claims County Deputy · Unit 06',badge:'FSP-0614',truth:'detain',intro:'A woman in a patrol jacket sits very still. “You know the procedure. Let me through.” The nameplate says WARD; the badge is already facing outward.',identity:'The card photo shows plain clothes, while the visitor wears a deputy patch. Badge FSP-0614 is identical to Aaron Pike’s. The printed name and the attached serial do not belong together.',purpose:'“I am Deputy Pike. I already told the other officer. You have exactly the same face he had.” She uses the wrong call sign for Unit 06.',records:'The roster says FSP-0614 belongs to Aaron Pike. Lena Ward has a civilian visitor permit only, and no law-enforcement appointment. The same visitor was denied entry eleven years ago under a different name.',openReply:'Her eyes move to the blank monitor. “It is okay. The camera always gets my name wrong.”'},
  {name:'Tomas Reed',role:'Licensed Electrical Contractor',badge:'CO-208',truth:'admit',intro:'A tired contractor rests a canvas tool bag beside the chair. “The generator ticket says I should report to the relay cabin. I need a signature for the call-out fee.”',identity:'Contractor permit CO-208 is active, photo and signature match, and the tamper strip is unbroken. The expiration time is tomorrow at 06:00.',purpose:'“I was sent to check the relay generator. Dispatch told me not to switch the radio off, even if I heard my own voice coming back.”',records:'Work order CO-208 was issued at 01:52. The maintenance log confirms the assignment. There is no duplicate credential or active warrant.',openReply:'He looks exhausted. “My tools keep ringing like a phone when nobody touches them. I did not bring a phone.”'},
  {name:'Dr. Irena Holt',role:'Claims County Clinic · Night Nurse',badge:'MED-773',truth:'detain',intro:'A pale woman in a nurse’s jacket stands on the wrong side of the waiting-room line. She does not blink when the overhead bulb fails.',identity:'The clinic credential reads IRENA HOLT, license MED-773. The face in the badge photograph looks directly at the camera; the visitor’s face is turned away in the same frame no matter how the card is tilted.',purpose:'“I came for the body you are keeping in Interview Room Two. It is awake again. You need to give it back before it remembers the rest of your name.”',records:'MED-773 was revoked in 2017. The license holder is listed deceased. No after-hours clinic transfer was authorized tonight, and the visitor pass was printed by a terminal that has been disconnected for three days.',openReply:'“There was a nurse here before me,” she whispers. “She said I could borrow her face until morning.”'},
  {name:'Owen Dyer',role:'County Records Clerk',badge:'COUNTY-017',truth:'admit',intro:'A thin clerk pushes a paper cup forward. No steam rises from it. “Records room. Overnight shift. Your visitor log has one extra line, and I was told to find out which one.”',identity:'County staff badge COUNTY-017 matches the photo, signature, and fingerprint record. The card has old lamination and a correctly stamped staff authorization.',purpose:'“I reconcile the after-hours visitor register. Six names were on the sheet when I left. The camera log says seven people came inside, but I only remember hearing six knocks.”',records:'Owen Dyer is scheduled from 22:00 to 04:00. His badge was used once at the staff entrance. No duplicate identity has been reported; his access pattern is consistent.',openReply:'He lowers his voice. “If the printer gives you a blank badge, do not throw it away. Something is using the blank side as a door.”'},
  {name:'DUPLICATE OFFICER',role:'Claims Same Active Patrol Identity',badge:'FSP-0007',truth:'detain',intro:'The final visitor looks exactly like you in the body-camera still. They wear your uniform and carry a flashlight that points the wrong way. “I have been guarding the inside door since before you started your shift.”',identity:'The personnel number FSP-0007 and photo match your active file exactly. The image timestamp is six minutes in the future. On the card, the figure’s shadow falls toward the light source.',purpose:'“You told me to wait behind you. You said you would come back for my body when the interview was over.”',records:'Only one FSP-0007 is authorized. Dispatch has your current unit in the swamp and never issued a second officer. The intake camera logs this visitor as entering from INSIDE the locked wall.',openReply:'The visitor moves their mouth after the voice ends. “You are the copy tonight. I am the one who came in first.”'}
];
function stationCurrentIndex(){return state.stationQueue[state.stationQueuePosition]}
function stationCurrentName(index){return index===5?specs[state.selectedCharacter].name:stationSuspects[index].name}
function stationScore(){return Object.entries(state.stationDecisions).reduce((total,[key,value])=>total+(stationSuspects[Number(key)]&&stationSuspects[Number(key)].truth===value?1:0),0)}
function stationQuestionCount(index){const checks=state.stationChecks[index]||{};return ['identity','purpose','records'].filter(k=>checks[k]).length}
function stationIsCorrect(index){return state.stationDecisions[index]&&stationSuspects[index]&&state.stationDecisions[index]===stationSuspects[index].truth}
function stationAppendChat(index,sender,text,kind=''){
  if(!state.stationChats[index])state.stationChats[index]=[];
  state.stationChats[index].push({sender,text,kind});
  if(state.stationChats[index].length>36)state.stationChats[index].splice(0,6);
  const log=$('stationChatLog');
  if(Number(stationCurrentIndex())===Number(index)){
    const line=document.createElement('div');
    line.className='station-line '+(kind||'');
    const senderNode=document.createElement('span');senderNode.className='station-sender';senderNode.textContent=sender;
    const textNode=document.createElement('span');textNode.textContent=text;
    line.appendChild(senderNode);line.appendChild(textNode);log.appendChild(line);log.scrollTop=log.scrollHeight;
  }
}
function openStationIntake(){
  if(state.floor!=='inside'||!state.room||state.room.id!=='station'){
    toast('THE INTAKE SYSTEM CAN ONLY BE USED INSIDE THE COUNTY POLICE STATION.',2.5);return;
  }
  if(state.stationStage==='idle'){
    state.stationStage='run';state.stationQueue=[0,1,2,3,4,5];state.stationQueuePosition=0;state.stationRetryMode=false;
  }
  audioStart();sound('radio');
  renderStationIntake();
  enterScreen('stationIntake');
}
function stationMakeSummary(){
  const score=stationScore();
  const processed=Object.keys(state.stationDecisions).length;
  const wrong=stationSuspects.map((s,i)=>i).filter(i=>state.stationDecisions[i]&& !stationIsCorrect(i));
  const auditHtml=state.stationAuditTrail.slice(-12).map(row=>'<div>'+escapeHTML(row.name)+' — '+escapeHTML(row.decision.toUpperCase())+' / '+(row.correct?'MATCH':'MISMATCH')+(row.review?' · REVIEW':'')+'</div>').join('');
  const title=state.stationStage==='complete'?'INTAKE LEDGER ACCEPTED':'AUDIT REQUIRED';
  let body='';
  if(state.stationStage==='complete'){
    body='<h3>'+title+'</h3><div class="station-score">VERIFIED DECISIONS: '+score+'/6 · VISITORS SCREENED: '+processed+'/6</div><p>The intake ledger has been sealed. The camera monitor shows an empty chair behind you, but its microphone keeps recording a second officer breathing.</p><p><b>CASE UNLOCKED:</b> The evidence board now includes the station’s duplicate-arrival report. You may close intake and return to the investigation.</p><p style="color:#c17b74">SYSTEM NOTICE: VISITOR 06 IS STILL INSIDE THE BUILDING.</p><div class="station-doc"><strong>PERMANENT AUDIT TRAIL</strong>\n'+auditHtml+'</div>';
    $('stationReviewFiles').classList.add('hidden');$('stationNextVisitor').classList.add('hidden');
    $('stationCaseView').classList.add('hidden');$('stationSummary').classList.remove('hidden');$('stationSummary').innerHTML=body;
    $('stationProgress').textContent='LEDGER SEALED';$('stationThreat').textContent='THREAT: UNRESOLVED';
    return;
  }
  if(state.stationStage==='reviewNeeded'){
    body='<h3>'+title+'</h3><div class="station-score">CORRECT DECISIONS: '+score+'/6 · AT LEAST 5 REQUIRED, DUPLICATE OFFICER MUST BE DETAINED</div><p>You recorded '+processed+' visitor decisions. '+wrong.length+' file(s) conflict with the available identity records. The intake system will not certify this report.</p><p>Study at least four physical clues in the case file [J] before reopening flagged files. You must inspect each file again; the previous answers will remain part of the audit log.</p><p class="station-alert">The monitor behind the clerk now shows '+escapeHTML(specs[state.selectedCharacter].name)+' standing in the corridor. Your character is still at the desk.</p><div class="station-doc"><strong>PERMANENT AUDIT TRAIL</strong>\n'+auditHtml+'</div>';
    $('stationReviewFiles').classList.remove('hidden');$('stationReviewFiles').disabled=studyCount()<4||wrong.length===0;
    $('stationNextVisitor').classList.add('hidden');$('stationCaseView').classList.add('hidden');$('stationSummary').classList.remove('hidden');$('stationSummary').innerHTML=body;
    $('stationProgress').textContent='AUDIT / '+wrong.length+' FLAGGED';$('stationThreat').textContent='THREAT: '+(state.stationThreat>2?'BREACH LIKELY':'UNSTABLE');
    return;
  }
  $('stationSummary').classList.add('hidden');$('stationCaseView').classList.remove('hidden');
}
function renderStationIntake(){
  stationMakeSummary();
  if(state.stationStage==='complete'||state.stationStage==='reviewNeeded')return;
  const index=stationCurrentIndex();
  if(index===undefined){finishStationBatch();return;}
  const suspect=stationSuspects[index];
  const checks=state.stationChecks[index]||(state.stationChecks[index]={identity:false,purpose:false,records:false});
  const answered=Object.prototype.hasOwnProperty.call(state.stationDecisions,index);
  $('stationProgress').textContent=(state.stationRetryMode?'AUDIT ':'VISITOR ')+(state.stationQueuePosition+1)+' / '+state.stationQueue.length+' · FILE '+String(index+1).padStart(2,'0');
  $('stationThreat').textContent='THREAT: '+(state.stationThreat>=3?'BREACH LIKELY':state.stationThreat>=1?'UNSTABLE':'CONTAINED');
  $('stationFeedTitle').textContent=index===5?'CAM 04 · INNER WALL':index>=3?'CAM 04 · SIGNAL DELAY':'INTAKE WINDOW B';
  $('stationFeedStatus').textContent=index===5?'REC ● / NO DOOR EVENT':index>=3?'REC ● / SYNC LOST':'REC ●';
  $('stationIntakePanel').classList.toggle('breach-mid',index>=3||state.stationThreat>=2);
  $('stationIntakePanel').classList.toggle('breach-final',index===5||state.stationThreat>=4);
  $('stationSuspectName').textContent=stationCurrentName(index);
  $('stationSuspectRole').textContent=suspect.role;
  $('stationZoomInterview').disabled=answered;
  $('stationZoomInterview').textContent=answered?'INTERVIEW FILE CLOSED':'ONE-ON-ONE / CAMERA CLOSE-UP';
  $('stationPortrait').classList.toggle('anomaly',(state.stationChecks[index]&&state.stationChecks[index].records&&suspect.truth==='detain')||index===5||(state.stationThreat>=4&&index>=3));
  $('stationIdCard').innerHTML='<strong>DOCUMENT SCAN</strong>\nName: '+(checks.identity?escapeHTML(stationCurrentName(index)):'████████')+'\nID number: '+(checks.identity?escapeHTML(suspect.badge):'NOT INSPECTED')+'\nPhoto match: '+(checks.identity?'SEE INSPECTION NOTES':'UNCONFIRMED')+'\nAuthorization: '+(checks.records?'ROSTER CHECKED':'NOT CHECKED');
  $('stationRegistryCard').innerHTML='<strong>ROSTER RESPONSE</strong>\n'+(checks.records?escapeHTML(suspect.records):'Awaiting database query.');
  const count=stationQuestionCount(index);
  $('stationSuspectStatus').textContent=answered?'DECISION RECORDED: '+state.stationDecisions[index].toUpperCase()+'. '+(stationIsCorrect(index)?'The decision matches the records.':'The recorded decision conflicts with the evidence.'):'INSPECTIONS COMPLETE: '+count+'/3. You must inspect the ID, question the visitor, and cross-check the roster before deciding.';
  for(const button of document.querySelectorAll('[data-station-ask]')){
    const kind=button.dataset.stationAsk;
    button.classList.toggle('checked',!!checks[kind]);
    button.disabled=answered;
  }
  for(const button of document.querySelectorAll('[data-station-decision]'))button.disabled=count<3||answered;
  $('stationNextVisitor').classList.toggle('hidden',!answered);
  $('stationDecisionButtons').classList.toggle('hidden',answered);
  $('stationReviewFiles').classList.add('hidden');
  $('stationFeedback').className='station-feedback'+(answered?(stationIsCorrect(index)?' good':' bad'):'');
  $('stationFeedback').textContent=state.stationFeedback||'No decision recorded. The visitor is waiting.';
  const topics=state.stationTopics[index]||(state.stationTopics[index]={});
  for(const button of document.querySelectorAll('[data-station-topic]')){button.classList.toggle('checked',!!topics[button.dataset.stationTopic]);button.disabled=answered;}
  const incident=$('stationIncidentBanner');
  if(index>=5){incident.classList.remove('hidden');incident.textContent='UNAUTHORIZED FEED: The last visitor appears on camera behind the officer. The room behind the officer is empty.';}
  else if(index>=3||state.stationThreat>=2){incident.classList.remove('hidden');incident.textContent='SIGNAL DRIFT: Camera 04 is recording '+(index+1)+' visitor(s). The audio track contains an extra set of footsteps.';}
  else{incident.classList.add('hidden');incident.textContent='';}
  const log=$('stationChatLog');
  log.innerHTML='';
  const entries=state.stationChats[index]||[];
  if(!entries.length){
    state.stationChats[index]=[{sender:stationCurrentName(index),text:suspect.intro,kind:''}];
  }
  if(index>=3&&!state.stationManifestEvents['camera-rewrite']){
    state.stationManifestEvents['camera-rewrite']=true;
    state.stationThreat=Math.max(state.stationThreat,2);
    state.stationChats[index].push({sender:'CAMERA 04',text:'TIMESTAMP REWRITTEN: The visitor entered at 02:17. The same frame shows them leaving at 02:16.',kind:'system'});
    if(state.options.voiceWhispers)triggerWhisper('You cannot leave before you arrive.','behind','CAMERA 04');
  }
  if(index===5&&!state.stationManifestEvents['duplicate-officer']){
    state.stationManifestEvents['duplicate-officer']=true;
    state.stationThreat=5;
    state.stationChats[index].push({sender:'CAMERA 04',text:'UNAUTHORIZED FEED: The same officer is visible behind the glass. The seat in front of you is empty.',kind:'system'});
    state.disappearanceLog.push('At the police station, the camera recorded the active officer in two locations at once.');
    if(state.options.voiceWhispers)triggerWhisper('Do not admit yourself.','center','CAMERA 04');
  }
  for(const entry of state.stationChats[index]){
    const line=document.createElement('div');line.className='station-line '+(entry.kind||'');
    const sender=document.createElement('span');sender.className='station-sender';sender.textContent=entry.sender;
    const message=document.createElement('span');message.textContent=entry.text;
    line.appendChild(sender);line.appendChild(message);log.appendChild(line);
  }
  log.scrollTop=log.scrollHeight;
  $('stationChatInput').disabled=answered;
}
function openSuspectZoom(){
  if(state.screen!=='stationIntake')return;
  const index=stationCurrentIndex();
  const suspect=stationSuspects[index];
  if(index===undefined||!suspect||state.stationDecisions[index])return;
  $('suspectZoomName').textContent=stationCurrentName(index);
  $('suspectZoomRole').textContent=suspect.role+' · FILE '+String(index+1).padStart(2,'0')+' / SIX';
  $('suspectZoomLine').textContent=suspect.intro;
  $('suspectZoomResponse').textContent='The suspect is close enough that the camera microphone records their breathing separately from the station room tone. Choose a question.';
  $('suspectZoomCameraStatus').textContent='CAM 04 AUTO-ZOOM · '+(state.stationThreat>=3?'FOCUS LOST / FACE TRACKING':'AUDIO OPEN / FRAME HOLD');
  const figure=$('suspectZoomFigure');
  figure.classList.toggle('anomaly',suspect.truth==='detain'||index>=3||state.stationThreat>=3);
  figure.style.setProperty('--zoom-seed',String(index+1));
  $('suspectZoomPanel').classList.remove('hidden');
  $('suspectZoomChoices').querySelectorAll('button').forEach(button=>button.disabled=false);
  $('closeSuspectZoom').focus({preventScroll:true});
  sound('radio');
  state.intensity=Math.max(state.intensity,.42);
}
function handleSuspectZoomChoice(action){
  if(state.screen!=='stationIntake'||$('suspectZoomPanel').classList.contains('hidden'))return;
  const index=stationCurrentIndex();
  const suspect=stationSuspects[index];
  if(index===undefined||!suspect||state.stationDecisions[index])return;
  const actions={identity:()=>stationInspect('identity',true),purpose:()=>stationInspect('purpose',true),records:()=>stationInspect('records',true),camera:()=>stationAskTopic('camera',true),extra:()=>stationAskTopic('extra',true),silas:()=>stationAskTopic('silas',true)};
  if(!actions[action])return;
  actions[action]();
  const entries=state.stationChats[index]||[];
  const last=entries[entries.length-1];
  $('suspectZoomResponse').textContent=last?last.text:'The room microphone records a second breath after the suspect stops speaking.';
  $('suspectZoomCameraStatus').textContent='CAM 04 · QUESTION LOGGED · '+(state.stationThreat>=4?'SUBJECT TRACKING LOST':'FRAME '+String(17+Math.floor(state.elapsed*3)).padStart(4,'0'));
  $('suspectZoomLine').textContent=state.stationThreat>=4?'Their expression does not change, but the reflection behind them turns toward the camera.':(last?last.text:suspect.openReply);
  const figure=$('suspectZoomFigure');
  figure.classList.remove('hit');
  void figure.offsetWidth;
  figure.classList.add('hit');
  figure.classList.toggle('anomaly',suspect.truth==='detain'||index>=3||state.stationThreat>=3);
  if(state.stationDecisions[index])$('suspectZoomChoices').querySelectorAll('button').forEach(button=>button.disabled=true);
}
function closeSuspectZoom(){
  $('suspectZoomPanel').classList.add('hidden');
  if(state.screen==='stationIntake')$('stationChatInput').focus({preventScroll:true});
}
function stationTopicReply(index,topic){
  const replies={
    camera:[
      'Camera 04 went dark at 02:17. A second feed appeared from inside the wall. I heard the camera motor turn, but that model has no motor.',
      'The camera sees me exactly as I am. Why does it keep showing an empty chair when I am sitting in it?',
      'I heard a shutter click. That camera has no shutter. The picture it printed was taken from behind the glass.',
      'The monitor showed me walking through this room three hours before I arrived. I told my supervisor. He said the timestamp was tomorrow.',
      'Six names are on the visitor sheet. The camera says seven. The seventh frame has your badge, but your seat is empty.',
      'Look at the camera feed. I am the one at the desk. You are the one standing in the corridor. It has always been that way.'
    ],
    extra:[
      'I was not the seventh visitor. I was number six. Do not let the system make me number seven.',
      'There are always seven. Six are permitted to leave. The seventh is the one who keeps the door shut.',
      'Someone left with my face and my tools. I stayed because my shadow was still on the floor.',
      'The seventh patient has no pulse, but the intercom keeps asking them to identify themselves.',
      'Six names. Seven knocks. Every time the clerk counts, someone else is standing in the doorway.',
      'You have not counted yourself. You keep counting the people who arrive, not the one who was already here.'
    ],
    silas:[
      'Silas told me not to use the side door. He said it only opens from the other side, even when you are outside.',
      'Silas told me your shift ended yesterday. He said the officer on duty today would look just like you.',
      'Silas gave me the generator key. It was warm, like someone had been holding it inside their mouth.',
      'Silas is above this room. I can hear him walking. I can also see him standing beside you.',
      'Silas said one of you would ask about him. He did not say which one was real.',
      'I interviewed Silas. He said he had never seen you before. He was lying to me, or he is lying to you.'
    ],
    door:[
      'I came through the front door, but I never heard it open. I remember the waiting room, then I was already seated.',
      'The side door was locked. Something on the other side said my name and the lock opened toward the wall.',
      'The contractor entrance opened onto the evidence room. The corridor was missing while I walked through it.',
      'There is no door behind you. I watched somebody step through that wall, and the wall closed around their coat.',
      'The visitor door was bricked over in 1994. The night guard still checks it every hour.',
      'You opened the door from this side before my badge scanned. I came in after you. I am sure of that.'
    ]
  };
  return (replies[topic]||replies.camera)[index]||'The visitor stares at the camera instead of answering. The microphone records your question twice.';
}
function stationAskTopic(topic,fromTyped=false){
  if(state.screen!=='stationIntake')return;
  const index=stationCurrentIndex();
  const suspect=stationSuspects[index];
  if(index===undefined||!suspect||state.stationDecisions[index])return;
  const topics=state.stationTopics[index]||(state.stationTopics[index]={});
  const labels={camera:'Ask about Camera 04',extra:'Ask about the extra arrival',silas:'Ask about Silas and the house',door:'Ask how the visitor entered'};
  if(!fromTyped)stationAppendChat(index,'OFFICER',labels[topic]+'.','officer');
  const reply=stationTopicReply(index,topic);
  stationAppendChat(index,stationCurrentName(index),topics[topic]?'You asked this already. The visitor repeats the answer with one word changed: '+reply:reply,topics[topic]?'system':'');
  if(!topics[topic]){
    topics[topic]=true;
    if(topic==='camera'||topic==='extra'){
      state.disappearanceLog.push('Station interview: '+stationCurrentName(index)+' described an extra camera arrival. Statement '+(index+1)+' was time-stamped twice.');
    }
    if(index>=3||topic==='extra'||topic==='camera'){
      state.stationThreat=Math.min(5,state.stationThreat+((index>=4||topic==='extra')?1:0));
      state.noise=Math.max(state.noise,.28);
      state.intensity=Math.min(1,state.intensity+.035);
    }
  }
  state.stationFeedback='FOLLOW-UP RECORDED: '+labels[topic].toUpperCase()+'. Compare the answer with the physical evidence before making your decision.';
  if(topic==='camera'&&index>=3&&state.options.voiceWhispers)triggerWhisper('Camera four has been looking from the inside.','behind','CAMERA 04 AUDIO');
  if(topic==='extra'&&index===5&&state.options.voiceWhispers)triggerWhisper('There was no first officer. There was only you.','center','DUPLICATE IDENTITY');
  sound('radio');
  renderStationIntake();
}
function stationInspect(kind,fromTyped=false){
  if(!state.running&&state.screen!=='stationIntake')return;
  if(state.screen!=='stationIntake')return;
  const index=stationCurrentIndex();
  const suspect=stationSuspects[index];
  if(index===undefined||!suspect||state.stationDecisions[index])return;
  const checks=state.stationChecks[index]||(state.stationChecks[index]={identity:false,purpose:false,records:false});
  const prompts={identity:'Let me inspect your ID, photograph, and credential number.',purpose:'Tell me exactly why you came to this station tonight.',records:'Cross-checking your details with the official duty roster.'};
  if(!fromTyped)stationAppendChat(index,'OFFICER',prompts[kind],'officer');
  stationAppendChat(index,stationCurrentName(index),suspect[kind]||suspect.openReply,'');
  checks[kind]=true;
  state.stationFeedback=kind==='records'?'Roster response received. Compare it with the badge and the statement before deciding.':kind==='identity'?'Document scan updated. Look for mismatched numbers, photographs, dates, and authorization.':'Statement recorded. Compare the visitor’s claim with the records.';
  sound('radio');
  renderStationIntake();
}
function sendStationChat(){
  const input=$('stationChatInput');
  if(!input||state.screen!=='stationIntake')return;
  const message=input.value.trim();
  if(!message)return;
  const index=stationCurrentIndex();
  const suspect=stationSuspects[index];
  if(index===undefined||!suspect||state.stationDecisions[index])return;
  input.value='';stationAppendChat(index,'OFFICER',message,'officer');
  const text=message.toLowerCase();
  let topic='';
  if(/camera|monitor|footage|video feed|security screen/.test(text))topic='camera';
  else if(/seventh|extra visitor|extra arrival|six people|seven people|seven knocks|visitor count/.test(text))topic='extra';
  else if(/silas|farmhouse|the house|missing deputy|witness/.test(text))topic='silas';
  else if(/which door|side door|front door|how did you enter|how did you get in|came through|entered the building|locked door/.test(text))topic='door';
  if(topic){stationAskTopic(topic,true);return;}
  let kind='';
  if(/badge|id card|photo|photograph|license|identity|name|serial/.test(text))kind='identity';
  else if(/record|roster|database|verify|verification|unit number|shift|dispatch log|permit/.test(text))kind='records';
  else if(/where|why|reason|purpose|doing|arrive|arrived|alibi|came here|here tonight|what happened/.test(text))kind='purpose';
  if(kind){
    stationInspect(kind,true);
    return;
  }
  const disturbing=/mirror|human|real|dead|reflection|shadow|copy|behind me|wall|voice|camera/.test(text);
  const response=disturbing?suspect.openReply:(suspect.truth==='detain'?'The visitor smiles without moving their cheeks. “You already wrote the answer down. You just have not looked at the paper yet.”':'The visitor considers the question. “Check the roster. Please do not make me repeat the entire night.”');
  stationAppendChat(index,stationCurrentName(index),response,disturbing?'system':'');
  if(disturbing){state.stationThreat=Math.min(5,state.stationThreat+1);state.noise=Math.max(state.noise,.3);state.intensity=Math.min(1,state.intensity+.06);}
  renderStationIntake();
}
function stationRecordDecision(decision){
  if(state.screen!=='stationIntake')return;
  const index=stationCurrentIndex();
  const suspect=stationSuspects[index];
  if(index===undefined||!suspect)return;
  if(stationQuestionCount(index)<3){
    toast('DECISION BLOCKED: INSPECT THE ID, ASK THE VISITOR, AND CROSS-CHECK THE ROSTER FIRST.',3.1);return;
  }
  state.stationDecisions[index]=decision;
  state.stationProcessed=Object.keys(state.stationDecisions).length;
  const correct=suspect.truth===decision;
  state.stationAuditTrail.push({index,name:stationCurrentName(index),decision,correct,review:state.stationRetryMode});
  if(correct){
    state.stationFeedback='DECISION ACCEPTED. '+(decision==='detain'?'The visitor is escorted to the holding room. The intake camera records an empty chair where they were sitting.':'The visitor is admitted under verified credentials. The security door opens one second before the badge is scanned.');
    state.stationCorrect=stationScore();
    stationAppendChat(index,'INTAKE SYSTEM',decision==='detain'?'DETENTION AUTHORIZED. HOLDING ROOM 2 LOCKED.':'ENTRY AUTHORIZED. ACCESS LOG SIGNED.', 'system');
  }else{
    state.stationThreat=Math.min(5,state.stationThreat+1);
    state.stationFeedback='DECISION DOES NOT MATCH THE RECORD. The security system accepts your command, but another interior door unlocks somewhere behind the desk.';
    state.noise=Math.max(state.noise,.5);state.intensity=Math.min(1,state.intensity+.16);state.flashlightFlickerTimer=Math.max(state.flashlightFlickerTimer||0,.85);
    stationAppendChat(index,'INTAKE SYSTEM','DECISION DISCREPANCY LOGGED. SECOND SIGNATURE DETECTED ON THE SAME FILE.','system');
    if(state.options.voiceWhispers&&state.stationThreat>=2)triggerWhisper('Thank you for letting me inside. I was getting tired of knocking.','behind','VOICE FROM HOLDING ROOM');
  }
  state.stationChats[index]=state.stationChats[index]||[];
  const entries=state.stationChats[index];
  const resultLine='FINAL DECISION: '+decision.toUpperCase()+' — '+(correct?'MATCH':'MISMATCH');
  stationAppendChat(index,'AUDIT LOGGER',resultLine,'system');
  sound(correct?'radio':'scare');
  renderStationIntake();
}
function stationNextVisitor(){
  if(state.screen!=='stationIntake')return;
  const index=stationCurrentIndex();
  if(index===undefined||!Object.prototype.hasOwnProperty.call(state.stationDecisions,index))return;
  state.stationQueuePosition++;
  state.stationFeedback='';
  if(state.stationQueuePosition>=state.stationQueue.length){finishStationBatch();return;}
  const next=stationCurrentIndex();
  if(!state.stationChats[next])state.stationChats[next]=[{sender:stationCurrentName(next),text:stationSuspects[next].intro,kind:''}];
  renderStationIntake();
}
function finishStationBatch(){
  const score=stationScore();
  state.stationCorrect=score;
  state.stationProcessed=Object.keys(state.stationDecisions).length;
  if(score>=5&&state.stationDecisions[5]==='detain'){
    state.stationComplete=true;state.stationStage='complete';state.stationFeedback='';
    if(!state.stationIncidentLogged){
      state.stationIncidentLogged=true;
      const item={id:'station-intake-ledger',name:'County intake audit ledger',detail:'The six visitor files were screened against identity documents and the official roster.',analysis:'At least five decisions match the credential evidence. One visitor was linked to a duplicate badge and a camera feed timestamped in the future. The final intake record is signed by an unidentified second officer.',kind:'intake',studied:true};
      const existing=caseRecords.find(r=>r.id===item.id);if(existing)Object.assign(existing,item);else caseRecords.push(item);
      state.disappearanceLog.push('The intake terminal printed a seventh visitor entry after the ledger was sealed. The name field contains the active officer’s signature.');
    }
    state.noise=Math.max(state.noise,.45);state.intensity=1;state.flashlightFlickerTimer=Math.max(state.flashlightFlickerTimer||0,1.25);
    tone(68,.65,'sawtooth',.07,-20);
    if(state.options.voiceWhispers)triggerWhisper('You checked six people. The camera counted seven.','center','INTAKE CAMERA 04');
    toast('INTAKE LEDGER SEALED. FIVE OR MORE DECISIONS VERIFIED. THE SEVENTH ARRIVAL IS STILL UNACCOUNTED FOR.',4.6);
    updateObjectives();updateHUD();
  }else{
    state.stationStage='reviewNeeded';
    state.stationQueue=stationSuspects.map((s,i)=>i).filter(i=>state.stationDecisions[i]&&!stationIsCorrect(i));
    state.stationQueuePosition=0;
    state.stationRetryMode=false;
    state.stationFeedback='';
    state.stationThreat=Math.min(5,state.stationThreat+1);
    toast('INTAKE AUDIT FAILED. STUDY FOUR PHYSICAL CLUES, REOPEN FLAGGED FILES, AND DETAIN THE DUPLICATE OFFICER.',4.1);
  }
  renderStationIntake();
}
function reviewStationFiles(){
  if(state.screen!=='stationIntake'||state.stationStage!=='reviewNeeded')return;
  if(studyCount()<4){toast('AUDIT LOCKED: STUDY FOUR PHYSICAL CLUES FIRST ('+studyCount()+'/4).',3);return;}
  const wrong=stationSuspects.map((s,i)=>i).filter(i=>state.stationDecisions[i]&&!stationIsCorrect(i));
  if(!wrong.length){finishStationBatch();return;}
  state.stationQueue=wrong;
  state.stationQueuePosition=0;
  state.stationRetryMode=true;
  state.stationStage='review';
  state.stationFeedback='AUDIT MODE: compare each flagged visitor against newly studied physical evidence. Your previous decision is still in the permanent log.';
  for(const index of wrong){state.stationChecks[index]={identity:false,purpose:false,records:false};delete state.stationDecisions[index];}
  const index=wrong[0];state.stationChats[index]=[{sender:'AUDIT SYSTEM',text:'REVIEW REQUIRED. This file was flagged by the first decision. Examine the visitor again; the night-shift recording has changed.',kind:'system'}];
  renderStationIntake();
}
function beginWitnessInterview(target){
  if(state.witnessInterviewed&&state.witnessTrust>=2){toast('SILAS HAS ALREADY GIVEN A CORROBORATED STATEMENT. REVIEW THE CASE FILE [J].',3);return;}
  if(state.witnessInterviewed&&state.witnessTrust<2&&studyCount()<6){toast('SILAS’S STATEMENT IS UNRELIABLE. STUDY SIX CLUES BEFORE ASKING HIM AGAIN.',3.2);return;}
  if(state.witnessInterviewed&&state.witnessTrust<2){state.witnessInterviewed=false;state.witnessTrust=0;state.interviewStep=0;state.interviewAwaitingContinue=false;state.interviewChoiceFeedback='';toast('SILAS WILL REOPEN HIS STATEMENT, BUT HE WILL NOT WAIT FOREVER.',3.0);}
  state.interviewStep=0;
  state.interviewAwaitingContinue=false;
  state.interviewChoiceFeedback='';
  audioStart();
  sound('radio');
  renderWitnessInterview();
  enterScreen('interview');
}
function renderWitnessInterview(){
  const prompts=[
    '“I did not call for help,” Silas says. “The call came from the house after the house was empty.” How do you establish his timeline?',
    'A burst of static rolls through the recorder. Silas flinches before the sound begins. What do you ask about the second voice?',
    'Silas looks toward the stairs. “It takes things first. Little things. Then the things you need to prove it was ever here.” How do you press him?'
  ];
  const choices=[
    [
      {label:'Let him explain in his own words.',trust:1,text:'Silas relaxes slightly. He says he waited near the kitchen until the radio called him by his childhood nickname. He insists he never gave that name to the deputy.'},
      {label:'Ask for a precise time and compare it with the patrol log.',trust:2,text:'You read back the conflicting times. Silas admits the call arrived before the lights went out, not after. Your calm cross-check makes him more cooperative.'},
      {label:'Accuse him of staging the whole scene.',trust:-2,text:'Silas goes silent. “That is what the thing wants you to write.” He refuses to give a reliable timeline.'}
    ],
    [
      {label:'Ask about the second voice beneath dispatch.',trust:2,requires:'radio',text:'Silas admits it copied the last words of everyone who entered the house. He heard the voice answer a question that nobody had asked yet.'},
      {label:'Play the cracked radio evidence and let the silence sit.',trust:2,requires:'radio',text:'The recording repeats your breathing before you breathe. Silas gives you a second location: the upstairs landing.'},
      {label:'Tell him the voice is just radio interference.',trust:-2,text:'He stares at you for several seconds. “Then why does it know who is alone?” His statement becomes less precise.'}
    ],
    [
      {label:'Show him the clues and ask what has gone missing.',trust:2,requires:'anyStudy',text:'Silas describes a brass key, a family photograph, and a deputy’s notebook vanishing one after another. He believes the disappearances mark where the thing has been.'},
      {label:'Ask what he saw upstairs without suggesting an answer.',trust:1,text:'He describes a shape at the end of the hall that was visible only in the dark window reflection. He never saw it turn around.'},
      {label:'Threaten to arrest him unless he tells you everything.',trust:-2,text:'Silas agrees with every accusation, but his answers contradict themselves. The statement is recorded as unreliable.'}
    ]
  ];
  const step=state.interviewStep;
  const closeFace=$('silasCloseFace');
  if(closeFace)closeFace.classList.toggle('unsettled',state.witnessTrust<0||state.interviewAwaitingContinue&&state.witnessTrust<1||step>=2);
  const closeCaption=$('silasZoomCaption');
  if(closeCaption){
    if(state.interviewAwaitingContinue)closeCaption.textContent=state.interviewChoiceFeedback;
    else if(step===0)closeCaption.textContent='SILAS IS LOOKING PAST YOUR SHOULDER. THE CAMERA SHOWS AN EMPTY DOORWAY.';
    else if(step===1)closeCaption.textContent='THE STATIC HAS STOPPED. SILAS STILL FLINCHES AT THE SOUND THAT IS NO LONGER PLAYING.';
    else if(step===2)closeCaption.textContent='HE HAS NOT MOVED HIS EYES ONCE. THE REFLECTION IN THE WINDOW IS BLINKING.';
    else closeCaption.textContent='RECORDING COMPLETE. A SECOND BREATH CONTINUES AFTER SILAS STOPS.';
  }
  const question=$('interviewQuestion');
  const buttons=$('interviewChoices');
  const feedback=$('interviewFeedback');
  const next=$('interviewContinue');
  const save=$('endInterview');
  const leave=$('leaveInterview');
  if(step>=3){
    question.innerHTML='<b>STATEMENT CONCLUSION</b><br>Silas signs the last page, then asks why the pen is still writing. The ink forms your badge number without your hand touching it.';
    buttons.innerHTML='';
    feedback.textContent=state.witnessTrust>=2?'STATEMENT STATUS: PARTLY CORROBORATED. His timeline has usable details, but one part remains impossible.':'STATEMENT STATUS: UNRELIABLE. The timeline is incomplete. Compare it against your collected evidence.';
    next.classList.add('hidden');
    save.classList.remove('hidden');
    leave.classList.add('hidden');
    return;
  }
  question.innerHTML='<b>QUESTION '+(step+1)+' / 3</b><br>'+escapeHTML(prompts[step]);
  feedback.textContent=state.interviewAwaitingContinue?state.interviewChoiceFeedback:'Choose how to question the witness. Answers can improve or damage the reliability of his statement.';
  if(state.interviewAwaitingContinue){
    buttons.innerHTML='';
    next.classList.remove('hidden');
    save.classList.add('hidden');
    leave.classList.add('hidden');
  }else{
    next.classList.add('hidden');
    save.classList.add('hidden');
    leave.classList.remove('hidden');
    buttons.innerHTML=choices[step].map((c,i)=>'<button type="button" data-witness-choice="'+i+'">'+escapeHTML(c.label)+'</button>').join('');
  }
}
function answerWitness(index){
  if(state.interviewAwaitingContinue||state.interviewStep>=3)return;
  const choices=[
    [
      {label:'Let him explain in his own words.',trust:1,text:'Silas relaxes slightly. He says he waited near the kitchen until the radio called him by his childhood nickname.'},
      {label:'Ask for a precise time and compare it with the patrol log.',trust:2,text:'You compare the conflicting times. Silas admits the call arrived before the lights went out. Your method earns a more useful statement.'},
      {label:'Accuse him of staging the whole scene.',trust:-2,text:'Silas shuts down. “That is what the thing wants you to write.” He refuses to give a reliable timeline.'}
    ],
    [
      {label:'Ask about the second voice beneath dispatch.',trust:caseRecords.some(r=>r.id==='radio'&&r.studied)?2:0,text:caseRecords.some(r=>r.id==='radio'&&r.studied)?'Your radio analysis supports the question. Silas admits the voice copied people before they spoke.':'Without studying the radio, Silas says you have no proof of a second voice.'},
      {label:'Play the cracked radio evidence and let the silence sit.',trust:caseRecords.some(r=>r.id==='radio'&&r.studied)?2:0,text:caseRecords.some(r=>r.id==='radio'&&r.studied)?'The recording repeats your breathing before you breathe. Silas gives you a second location: the upstairs landing.':'The evidence is bagged but unexamined. Silas refuses to interpret it for you.'},
      {label:'Tell him the voice is just radio interference.',trust:-2,text:'He stares at you. “Then why does it know who is alone?” His statement becomes less reliable.'}
    ],
    [
      {label:'Show him the clues and ask what has gone missing.',trust:studyCount()>=1?2:0,text:studyCount()>=1?'Silas describes a brass key, a family photograph, and a deputy’s notebook vanishing one after another. He thinks the disappearances mark where the thing has been.':'You have not studied any clues. Silas asks you to bring him something concrete before he risks saying more.'},
      {label:'Ask what he saw upstairs without suggesting an answer.',trust:1,text:'He describes a shape at the end of the hall, visible only in the dark window reflection. He never saw it turn around.'},
      {label:'Threaten to arrest him unless he tells you everything.',trust:-2,text:'Silas agrees with every accusation, but his answers contradict themselves. The statement is recorded as unreliable.'}
    ]
  ];
  const choice=choices[state.interviewStep][index];
  if(!choice)return;
  state.witnessTrust+=choice.trust;
  state.interviewChoiceFeedback=choice.text;
  state.interviewAwaitingContinue=true;
  sound('radio');
  renderWitnessInterview();
}
function continueWitnessInterview(){
  if(!state.interviewAwaitingContinue)return;
  state.interviewStep++;
  state.interviewAwaitingContinue=false;
  state.interviewChoiceFeedback='';
  renderWitnessInterview();
}
function finishWitnessInterview(){
  if(state.witnessInterviewed)return;
  state.witnessInterviewed=true;
  const reliable=state.witnessTrust>=2;
  const record={id:'silas-statement',name:'Silas Venn — recorded statement',detail:reliable?'The statement is partly corroborated, with one unexplained timeline gap.':'The statement contains contradictions and requires comparison against physical evidence.',analysis:reliable?'Silas heard the radio imitate a person before that person arrived. He reports three objects disappearing in sequence. His description of the upstairs reflection matches the waterlogged patrol log.':'Silas changed his timeline under pressure. His account cannot stand alone, but it still identifies the upstairs landing and a sequence of missing objects as leads.',kind:'statement',studied:false};
  const priorStatement=caseRecords.find(r=>r.id==='silas-statement');
  if(priorStatement)Object.assign(priorStatement,record);else caseRecords.push(record);
  if(state.room){const witness=state.room.items.find(i=>i.type==='witness');if(witness){witness.found=true;if(witness.id){state.roomItemStates=state.roomItemStates||{};state.roomItemStates[witness.id]={found:true,missing:false};}}}
  state.noise=Math.max(state.noise,.28);
  state.intensity=Math.min(1,state.intensity+.15);
  toast(reliable?'STATEMENT SAVED: PARTLY CORROBORATED. COMPARE IT WITH THE FORENSIC REPORTS.':'STATEMENT SAVED: UNRELIABLE. YOU NEED STRONGER PHYSICAL EVIDENCE.',4);
  queueStoryScare('personnel','silasImpossibleStatement',1.4);
  tone(210,.25,'sawtooth',.06,-95);
  updateObjectives();
  updateHUD();
  closeOverlay();
}
function openInventory(){
  if(!state.running)return;
  updateInventory();
  enterScreen('inventory');
}
function reloadWeapon(){
  if(reloadTimer>0)return;
  if(ammo>=6){toast('MAGAZINE ALREADY FULL.',1.2);return;}
  if(reserve<=0){toast('NO SPARE AMMUNITION.',1.5);return;}
  reloadTimer=.78;
  state.reloadActive=true;
  sound('reload');
  toast('RELOADING...',.9);
}
function shoot(){
  if(!state.running||state.paused||state.gameOver||state.floor==='inside')return;
  if(shootTimer>0||reloadTimer>0)return;
  if(ammo<=0){toast('CLICK. RELOAD WITH R.',1.1);tone(180,.05,'square',.04,-80);return;}
  audioStart();
  shootTimer=.27;
  ammo--;
  state.shots++;
  state.noise=1;
  state.intensity=Math.min(1,state.intensity+.14);
  sound('shot');
  state.screenShake=state.options.shake?.10:0;
  const target=worldCoordinates(pointer.x,pointer.y);
  const a=angleTo(player.x,player.y,target.x,target.y);
  player.angle=a;
  bullets.push({x:player.x+Math.cos(a)*17,y:player.y+Math.sin(a)*17,vx:Math.cos(a)*620,vy:Math.sin(a)*620,life:.72,owner:'player',r:3});
  for(let i=0;i<9;i++){
    addParticle({x:player.x+Math.cos(a)*16,y:player.y+Math.sin(a)*16,vx:Math.cos(a+Math.random()-.5)*(60+Math.random()*150),vy:Math.sin(a+Math.random()-.5)*(60+Math.random()*150),life:.15+Math.random()*.18,color:choose(['#f6daa2','#c7ab69','#f5e9c7']),size:1+Math.random()*2});
  }
  updateHUD();
}
function damagePlayer(amount,source){
  if(player.invulnerable>0||state.gameOver)return;
  player.hp=Math.max(0,player.hp-amount);
  health=player.hp;
  player.invulnerable=.65;
  state.damageFlash=.7;
  state.screenShake=state.options.shake?.25:0;
  state.noise=1;
  sound('hurt');
  toast(source==='smiler'?'IT IS RIGHT BEHIND YOU.':'SOMETHING BITES THROUGH YOUR UNIFORM.',1.6);
  updateHUD();
  if(player.hp<=0)finishGame(false);
}
function movePlayer(dt){
  if(state.hideSpotActive){player.moving=false;stamina=Math.min(player.maxStamina,stamina+7*dt);return;}
  if(state.personalScareTimer>0){player.moving=false;return;}
  if(state.floor==='inside'){
    moveInteriorPlayer(dt);
    return;
  }
  let dx=(keys.d||keys.arrowright?1:0)-(keys.a||keys.arrowleft?1:0);
  let dy=(keys.s||keys.arrowdown?1:0)-(keys.w||keys.arrowup?1:0);
  if(Math.abs(dx)+Math.abs(dy)>0){
    const len=Math.hypot(dx,dy)||1;
    dx/=len;
    dy/=len;
    player.moving=true;
    const wantsRun=keys.shift||touchRun;
    const running=wantsRun&&stamina>2;
    state.adaptiveHorror.sprintExposure=running?Math.min(65,state.adaptiveHorror.sprintExposure+dt):Math.max(0,state.adaptiveHorror.sprintExposure-dt*.32);
    const speed=player.speed*(running?1.55:1);
    if(running){
      stamina=Math.max(0,stamina-26*dt);
      state.noise=Math.max(state.noise,.58);
    }else{
      stamina=Math.min(player.maxStamina,stamina+17*dt);
      state.noise=Math.max(state.noise,.15);
    }
    const nx=player.x+dx*speed*dt;
    const ny=player.y+dy*speed*dt;
    if(!blockedAt(nx,player.y,player.r))player.x=nx;
    if(!blockedAt(player.x,ny,player.r))player.y=ny;
    player.angle=angleTo(0,0,dx,dy);
    player.step+=dt*(running?13:8);
    footstepTimer+=dt*(running?1.6:1);
    if(footstepTimer>(running?.28:.52)){
      footstepTimer=0;
      if(Math.random()<.6)sound('step');
    }
    if(running)state.intensity=Math.min(1,state.intensity+dt*.03);
  }else{
    player.moving=false;
    stamina=Math.min(player.maxStamina,stamina+21*dt);
    state.noise=Math.max(0,state.noise-dt*.5);
  }
  player.x=clamp(player.x,22,WORLD.w-22);
  player.y=clamp(player.y,22,WORLD.h-22);
}
function blockedAt(x,y,r){
  const onTrail=nearFootpath(x,y,56);
  const minX=Math.floor((x-r-13)/128),maxX=Math.floor((x+r+13)/128);
  const minY=Math.floor((y-r-13)/128),maxY=Math.floor((y+r+13)/128);
  for(let gx=minX;gx<=maxX;gx++)for(let gy=minY;gy<=maxY;gy++){
    const bucket=treeGrid.get(gx+','+gy);
    if(!bucket)continue;
    for(const t of bucket){
      if(Math.abs(t.x-x)>r+10||Math.abs(t.y-y)>r+12)continue;
      if(!onTrail&&dist(x,y,t.x,t.y)<r+6.7*t.s)return true;
    }
  }
  for(const o of objects){
    if(o.type!=='building')continue;
    if(Math.abs(o.x-x)<o.w/2+r&&Math.abs(o.y-y)<o.h/2+r)return true;
  }
  return false;
}
function moveInteriorPlayer(dt){
  if(!state.room)return;
  if(state.hideSpotActive){player.moving=false;return;}
  const dx=(keys.d||keys.arrowright?1:0)-(keys.a||keys.arrowleft?1:0);
  const dy=(keys.s||keys.arrowdown?1:0)-(keys.w||keys.arrowup?1:0);
  const len=Math.hypot(dx,dy)||1;
  if(dx||dy){
    const wantsRun=keys.shift||touchRun;
    const running=wantsRun&&stamina>2;
    state.adaptiveHorror.sprintExposure=running?Math.min(65,state.adaptiveHorror.sprintExposure+dt):Math.max(0,state.adaptiveHorror.sprintExposure-dt*.32);
    const moveSpeed=player.speed*(running?1.32:1);
    if(running)stamina=Math.max(0,stamina-17*dt);else stamina=Math.min(player.maxStamina,stamina+21*dt);
    const nx=player.x+dx/len*moveSpeed*dt;
    const ny=player.y+dy/len*moveSpeed*dt;
    if(!insideBlocked(nx,player.y))player.x=nx;
    if(!insideBlocked(player.x,ny))player.y=ny;
    player.angle=Math.atan2(dy,dx);
    player.moving=true;
    player.step+=dt*8;
  }else player.moving=false;
  player.x=clamp(player.x,32,state.room.w-32);
  player.y=clamp(player.y,32,state.room.h-32);
}
function insideBlocked(x,y){
  if(!state.room)return false;
  if(x<23||y<23||x>state.room.w-23||y>state.room.h-23)return true;
  const r=player&&player.r?player.r:9;
  for(const p of state.room.props){
    const left=p.x-p.w/2, right=p.x+p.w/2, top=p.y-p.h/2, bottom=p.y+p.h/2;
    const nearestX=clamp(x,left,right);
    const nearestY=clamp(y,top,bottom);
    if(dist(x,y,nearestX,nearestY)<r+2)return true;
  }
  return false;
}
function updateSurvivors(dt){
  const extraction=objects.find(o=>o.type==='exit');
  for(const s of survivors){
    if(!s.following||s.delivered)continue;
    let d=dist(player.x,player.y,s.x,s.y);
    if(state.floor==='outside'&&d>440){
      s.x=clamp(player.x-Math.cos(player.angle)*72+(s.id==='ana'?-18:18),48,WORLD.w-48);
      s.y=clamp(player.y-Math.sin(player.angle)*72+18,48,WORLD.h-48);
      d=dist(player.x,player.y,s.x,s.y);
    }
    if(state.floor==='outside'&&d>58){
      const a=angleTo(s.x,s.y,player.x,player.y);
      const speed=d>220?125:82;
      const nx=s.x+Math.cos(a)*speed*dt;
      const ny=s.y+Math.sin(a)*speed*dt;
      if(!blockedAt(nx,s.y,7))s.x=nx;
      if(!blockedAt(s.x,ny,7))s.y=ny;
    }
    if(extraction&&state.floor==='outside'&&dist(s.x,s.y,extraction.x,extraction.y)<115){
      s.delivered=true;
      s.following=false;
      state.rescued++;
      sound('pickup');
      toast(s.name.toUpperCase()+' REACHED THE SAFE ZONE.',2.3);
      updateObjectives();
      updateHUD();
    }
  }
}
function updateCrawlers(dt){
  if(state.floor==='inside')return;
  for(const c of crawlers){
    if(c.dead)continue;
    c.phase+=dt;
    c.attack=Math.max(0,c.attack-dt);
    c.stunned=Math.max(0,(c.stunned||0)-dt);
    if(c.stunned>0)continue;
    const d=dist(player.x,player.y,c.x,c.y);
    const range=state.floor==='inside'?0:270;
    if(player.hidden&&state.noise<.68){
      if(state.hideSpotActive&&d<140)state.hideRisk=Math.min(4,(state.hideRisk||0)+dt*.34);
      if(d<108&&state.elapsed>(state.crawlerSearchToastAt||0)){
        state.crawlerSearchToastAt=state.elapsed+5.2;
        toast('A CRAWLER SNIFFS THE COVER. DO NOT MOVE.',1.9);
      }
      continue;
    }
    if(d<range){
      c.alert=true;
      const a=angleTo(c.x,c.y,player.x,player.y);
      const speed=c.speed*(d<100?1.2:1);
      const nx=c.x+Math.cos(a)*speed*dt;
      const ny=c.y+Math.sin(a)*speed*dt;
      if(!blockedAt(nx,c.y,c.r))c.x=nx;
      if(!blockedAt(c.x,ny,c.r))c.y=ny;
      if(d<c.r+player.r+5&&c.attack<=0){
        c.attack=1.3;
        damagePlayer(13+Math.min(5,state.threatTier||0),'crawler');
      }
    }else if(Math.sin(c.phase*.7)>.94){
      c.x+=Math.cos(c.phase)*18*dt;
      c.y+=Math.sin(c.phase*.8)*18*dt;
    }
  }
}
function updateMonster(dt){
  if(!monster.active)return;
  monster.phase+=dt;
  monster.stun=Math.max(0,monster.stun-dt);
  monster.attack=Math.max(0,monster.attack-dt);
  monster.warpCooldown=Math.max(0,monster.warpCooldown-dt);
  monster.reappearGlow=Math.max(0,(monster.reappearGlow||0)-dt);
  if(state.floor==='outside'){
    if(monster.hidden){
      monster.vanishTimer-=dt;
      if(monster.vanishTimer<=0){
        monster.x=monster.pendingX;
        monster.y=monster.pendingY;
        monster.hidden=false;
        monster.activeTime=0;
        monster.reappearGlow=1.65;
        state.flashlightFlickerTimer=Math.max(state.flashlightFlickerTimer||0,.72);
        monster.attack=Math.max(monster.attack,.75);
        state.intensity=Math.max(state.intensity,.9);
        state.screenShake=Math.max(state.screenShake,.22);
        state.apparitionTimer=0;
        sound('radio');
        tone(42,.42,'sawtooth',.065,-30);
        for(let i=0;i<11;i++)addParticle({x:monster.x+(Math.random()-.5)*28,y:monster.y+(Math.random()-.5)*48,vx:(Math.random()-.5)*48,vy:-14-Math.random()*34,life:.35+Math.random()*.48,color:choose(['#581218','#8e2229','#c1bbaa']),size:2+Math.random()*2.5});
        if(state.options.voiceWhispers&&state.voiceCooldown<=0)triggerWhisper(choose(['You watched the place I left. Not the place I went.','The dark between us is shorter now.','I was standing there before you looked.','You keep turning toward the wrong sound.']),choose(['left','right']),'THE SMILER / SIGNAL RETURNS');
        toast(choose(['THE SMILER REAPPEARED SOMEWHERE ELSE.','IT IS BACK. IT DID NOT CROSS THE SPACE BETWEEN.','VISUAL CONTACT RESTORED. THE DISTANCE IS WRONG.']),3.0);
      }
      return;
    }
    monster.activeTime=(monster.activeTime||0)+dt;
    monster.vanishCooldown=Math.max(0,(monster.vanishCooldown||0)-dt);
    if(monster.activeTime>=(state.huntActive?2.6:3.5)&&monster.vanishCooldown<=0&&monster.stun<=0){
      let tx=monster.x,ty=monster.y,found=false;
      const referenceAngle=player.angle||0;
      for(let attempt=0;attempt<28;attempt++){
        const habits=state.adaptiveHorror||{};
        let angle;
        if((habits.sprintExposure||0)>12&&Math.random()<.55){angle=referenceAngle+(Math.random()-.5)*.95;}
        else if((habits.flashlightExposure||0)>23&&Math.random()<.68){angle=flashlightAngle()+(Math.random()<.5?-1:1)*(.34+Math.random()*.7);}
        else if((habits.hideCount||0)>=3&&Math.random()<.5){angle=Math.random()*Math.PI*2;}
        else{angle=Math.random()<.7?referenceAngle+Math.PI+(Math.random()-.5)*2.1:Math.random()*Math.PI*2;}
        const radius=(state.huntActive?145:195)+Math.random()*(state.huntActive?280:345);
        const candidateX=clamp(player.x+Math.cos(angle)*radius,65,WORLD.w-65);
        const candidateY=clamp(player.y+Math.sin(angle)*radius,65,WORLD.h-65);
        if(!blockedAt(candidateX,candidateY,monster.r+3)&&dist(player.x,player.y,candidateX,candidateY)>165){tx=candidateX;ty=candidateY;found=true;break;}
      }
      if(!found){
        const angle=player.angle+Math.PI+(Math.random()-.5)*1.8;
        tx=clamp(player.x+Math.cos(angle)*255,65,WORLD.w-65);
        ty=clamp(player.y+Math.sin(angle)*255,65,WORLD.h-65);
      }
      monster.pendingX=tx;
      monster.pendingY=ty;
      monster.hidden=true;
      monster.vanishTimer=state.huntActive?1.4+Math.random()*.95:2.25+Math.random()*1.65;
      monster.vanishCooldown=state.huntActive?4.2+Math.random()*3.4:6.5+Math.random()*5.8;
      monster.blinkCount=(monster.blinkCount||0)+1;
      state.intensity=Math.max(state.intensity,.88);
      state.noise=Math.max(state.noise,.28);
      state.screenShake=Math.max(state.screenShake,.2);
      state.apparitionTimer=0;
      sound('radio');
      tone(48,.5,'sawtooth',.075,-38);
      for(let i=0;i<9;i++)addParticle({x:monster.x+(Math.random()-.5)*30,y:monster.y+(Math.random()-.5)*52,vx:(Math.random()-.5)*58,vy:(Math.random()-.5)*50,life:.2+Math.random()*.34,color:choose(['#4e1117','#7c1e24','#bcc0a8']),size:2+Math.random()*3});
      if(state.options.voiceWhispers&&state.voiceCooldown<=0)triggerWhisper(choose(['It left the light. Count to one.','Do not search where it was.','It can move while your eyes are closed.','Listen for where the rain stops.']),choose(['left','right']),'THE SMILER / SIGNAL LOST');
      toast(choose(['THE SMILER HAS VANISHED. DO NOT TRUST THE EMPTY SPACE.','VISUAL CONTACT LOST. THE FOREST IS TOO QUIET.','IT DISAPPEARED. LISTEN — NOT EVEN THE FOOTSTEPS REMAIN.']),3.25);
      return;
    }
  }
  const d=dist(player.x,player.y,monster.x,monster.y);
  if(d<390)monster.spotted=true;
  if(player.hidden&&state.floor==='outside'&&state.noise<.68){
    if(d<125&&state.hideSpotActive){state.hideRisk+=dt*.18;}
    if(d<100&&state.elapsed>(state.hideSearchToastAt||0)){state.hideSearchToastAt=state.elapsed+4.8;toast('YOU HEAR IT SEARCHING THE OTHER SIDE OF THE TREE.',2.0);}
    return;
  }
  if(state.floor==='inside'){
    monster.frozenByLight=false;
    const apparition=state.indoorPresence;
    if(apparition&&apparition.timer>0){
      const roomDistance=dist(player.x,player.y,apparition.x,apparition.y);
      if(player.hidden&&state.hideSpotActive&&state.hideRisk<3.2){if(roomDistance<135)state.hideRisk+=dt*.65;return;}
      if(roomDistance<58&&monster.attack<=0){
        monster.attack=1.8;
        damagePlayer(15+Math.min(12,(state.threatTier||0)*2),'smiler');
        apparition.timer=0;
        apparition.cooldown=5.5;
        state.intensity=1;
        toast('IT WAS NOT A SHADOW. IT TOUCHED YOU.',2.8);
      }else if(roomDistance<145){
        state.intensity=Math.max(state.intensity,.8);
      }
    }
    return;
  }
  const towardMonster=angleTo(player.x,player.y,monster.x,monster.y);
  const beamDelta=Math.atan2(Math.sin(towardMonster-flashlightAngle()),Math.cos(towardMonster-flashlightAngle()));
  monster.frozenByLight=flashlight&&flashlightBattery>0&&d<505&&Math.abs(beamDelta)<.235;
  const slowedByLight=monster.frozenByLight&&d>58&&monster.stun<=0;
  if(monster.stun>0)return;
  const rescuedPressure=survivors.filter(s=>s.found||s.following||s.delivered).length;
  const huntRamp=Math.min(58,state.elapsed*.105+state.missingCount*4.1+evidence*3.4+rescuedPressure*7+(state.threatTier||0)*5);
  let speed=(d<280?126:state.noise>.3?108:78)+Math.min(44,evidence*3.5+rescuedPressure*9+state.elapsed/68)+huntRamp;
  if(state.anchorsDisabled&&state.elapsed<(state.monsterSuppressedUntil||0))speed*=.72;
  if(state.huntActive&&state.huntWarning<=0){speed*=1.39+Math.max(0,state.huntsTriggered-2)*.035;if(state.adaptiveHorror.sprintExposure>5)speed*=1.16;if(!player.moving&&!player.hidden)speed*=1.25;}
  if(state.finalManifestStarted&&state.extractionStarted&&state.extractionHold>=27&&state.extractionHold<30)speed*=1.18;
  if(state.adaptiveHorror.flashlightExposure>34&&!monster.frozenByLight)speed*=1.08;
  if(slowedByLight)speed*=state.huntActive?.78:.48;
  if(d>780&&state.noise<.2)monster.lastMove+=dt;
  else monster.lastMove=0;
  const a=angleTo(monster.x,monster.y,player.x,player.y);
  monster.x+=Math.cos(a)*speed*dt;
  monster.y+=Math.sin(a)*speed*dt;
  if(d<43&&monster.attack<=0){
    monster.attack=1.45;
    damagePlayer(28+Math.min(12,Math.floor(state.elapsed/115)*2)+Math.min(8,(state.threatTier||0)*2),'smiler');
    monster.x=clamp(monster.x-Math.cos(a)*44,30,WORLD.w-30);
    monster.y=clamp(monster.y-Math.sin(a)*44,30,WORLD.h-30);
  }
  if(d<250&&growlTimer<=0){
    sound('roar');
    growlTimer=5+Math.random()*6;
    if(Math.random()<.72)toast(choose(['YOU HEAR WET BREATHING OVER YOUR SHOULDER.','RADIO: DO NOT TURN AROUND.','SOMETHING SCRAPES ALONG THE TREES.','YOUR FLASHLIGHT JUST CAUGHT A SHAPE MOVING.']),1.8);
    state.intensity=Math.min(1,state.intensity+.18);
  }
}
function updateBullets(dt){
  for(const b of bullets){
    b.x+=b.vx*dt;
    b.y+=b.vy*dt;
    b.life-=dt;
    if(b.owner!=='player')continue;
    for(const c of crawlers){
      if(c.dead)continue;
      if(dist(b.x,b.y,c.x,c.y)<c.r+4){
        c.hp--;
        b.life=0;
        spawnBlood(c.x,c.y);
        if(c.hp<=0){
          c.dead=true;
          state.kills++;
          state.noise=Math.max(state.noise,.7);
          toast('MARSH CRAWLER NEUTRALIZED.',1.2);
        }
        break;
      }
    }
    if(monster.active&&!monster.hidden&&b.life>0&&dist(b.x,b.y,monster.x,monster.y)<monster.r+5){
      monster.stun=Math.max(monster.stun,1.4);
      b.life=0;
      spawnSparks(monster.x,monster.y);
      toast('THE SHAPE STAGGERS. IT DOES NOT FALL.',1.2);
    }
  }
  bullets=bullets.filter(b=>b.life>0);
  for(const p of particles){
    p.x+=p.vx*dt;
    p.y+=p.vy*dt;
    p.life-=dt;
    p.vx*=Math.pow(.07,dt);
    p.vy*=Math.pow(.07,dt);
  }
  particles=particles.filter(p=>p.life>0);
}
function spawnBlood(x,y){
  for(let i=0;i<7;i++)addParticle({x,y,vx:(Math.random()-.5)*160,vy:(Math.random()-.5)*160,life:.18+Math.random()*.4,color:choose(['#76302b','#a53b37','#47201d']),size:2+Math.random()*3});
}
function spawnSparks(x,y){
  for(let i=0;i<12;i++)addParticle({x,y,vx:(Math.random()-.5)*240,vy:(Math.random()-.5)*240,life:.12+Math.random()*.26,color:choose(['#d9c58e','#a2b28b','#efdfb2']),size:1+Math.random()*3});
}
function updateWeather(dt){
  state.lightningNext-=dt;
  if(state.lightningNext<=0){
    state.lightning=.15+Math.random()*.35;
    state.lightningNext=7+Math.random()*15;
    if(Math.random()<.5){
      setTimeout(()=>{state.lightning=Math.max(state.lightning,.08);},110);
    }
    if(Math.random()<.3)tone(40,.7,'triangle',.08,-8);
  }
  state.lightning=Math.max(0,state.lightning-dt*.7);
  state.damageFlash=Math.max(0,state.damageFlash-dt*1.8);
  $('damageFlash').style.opacity=state.damageFlash;
  state.screenShake=Math.max(0,state.screenShake-dt*.8);
  state.intensity=Math.max(0,state.intensity-dt*.035);
  for(const r of raindrops){
    r.y+=r.speed*dt;
    r.x-=r.speed*.16*dt;
    if(r.y>H+15){r.y=-15;r.x=Math.random()*W;}
    if(r.x<-15)r.x=W+10;
  }
  for(const f of fireflies)f.phase+=dt*f.speed;
}
function updateTrailPhantom(dt){
  if(!state.trailPhantom)state.trailPhantom={active:false,x:0,y:0,timer:0,cooldown:18,total:0,phase:0,kind:'edge'};
  const p=state.trailPhantom;
  p.phase+=dt;
  if(p.active){
    p.timer=Math.max(0,p.timer-dt);
    if(p.timer<=0){
      p.active=false;
      p.cooldown=13+Math.random()*16;
      if(Math.random()<.4){sound('radio');voiceNoise(choose(['left','right']),.055);}
      if(p.total%3===0&&state.options.voiceWhispers&&state.voiceCooldown<=0)triggerWhisper('You saw the part I wanted you to see.','behind','TREELINE / LAST FRAME');
    }
    return;
  }
  p.cooldown=Math.max(0,p.cooldown-dt);
  if(p.cooldown>0||state.elapsed<24||!monster||!monster.active||state.huntActive||state.radioIncidentActive||state.personalScareTimer>0||state.floor!=='outside'||p.total>=10)return;
  if(Math.random()>dt*.23)return;
  let found=false,tx=player.x,ty=player.y;
  for(let i=0;i<24;i++){
    let a;
    if(Math.random()<.62)a=(player.angle||0)+Math.PI+(Math.random()-.5)*1.75;
    else a=Math.random()*Math.PI*2;
    const radius=145+Math.random()*150;
    const cx=clamp(player.x+Math.cos(a)*radius,62,WORLD.w-62);
    const cy=clamp(player.y+Math.sin(a)*radius,62,WORLD.h-62);
    const trail=footpathDistance(cx,cy);
    if(!blockedAt(cx,cy,13)&&dist(player.x,player.y,cx,cy)>118&&trail>22&&trail<145){tx=cx;ty=cy;found=true;break;}
  }
  if(!found)return;
  p.active=true;p.x=tx;p.y=ty;p.timer=1.2+Math.random()*1.65;p.total++;p.kind=Math.random()<.48?'copy':'watcher';p.phase=Math.random()*12;
  state.intensity=Math.max(state.intensity,.68);state.noise=Math.max(state.noise,.22);
  state.flashlightFlickerTimer=Math.max(state.flashlightFlickerTimer||0,.28+Math.random()*.43);
  voiceNoise(choose(['left','right']),.045);
  if(Math.random()<.45)sound('step');
  if(state.options.voiceWhispers&&state.voiceCooldown<=0&&Math.random()<.55)triggerWhisper(choose(['It stands where the path stops.','There are too many trees to count, and one of them is breathing.','You found the trail. It found the trail first.','It is not in the woods. It is between the trees you remember.','The figure at the path edge is standing on the wrong side of the rain.']),choose(['left','right']),'FIELD CAMERA / FRAME MISSING');
  if(p.total%3===0)toast('A FIGURE IS STANDING BESIDE THE FOOTPATH. DO NOT ASSUME IT IS THE SMILER.',2.8);
}
function drawTrailPhantom(){
  const p=state.trailPhantom;
  if(!p||!p.active||state.floor!=='outside'||state.prologueStage!=='swamp')return;
  const x=p.x-camera.x+shakeX,y=p.y-camera.y+shakeY;
  if(x<-75||y<-110||x>W+75||y>H+110)return;
  const d=dist(player.x,player.y,p.x,p.y);
  const flick=Math.sin(state.elapsed*31+p.phase*7);
  const fade=Math.min(1,p.timer*4.5);
  ctx.save();ctx.globalAlpha=fade*(d<200?.9:.72);
  ctx.translate(Math.round(x),Math.round(y));
  const lean=Math.sin(p.phase*3.7)*4;
  ctx.fillStyle='#010201';
  ctx.beginPath();ctx.moveTo(-8,-59);ctx.lineTo(8,-62);ctx.lineTo(13,-45);ctx.lineTo(8,-20);ctx.lineTo(17,14);ctx.lineTo(8,15);ctx.lineTo(1,-4);ctx.lineTo(-5,18);ctx.lineTo(-17,25);ctx.lineTo(-13,-12);ctx.lineTo(-18,-40);ctx.closePath();ctx.fill();
  px(-8+lean,-69,16,19,'#010201');px(-11+lean,-62,22,12,'#020302');
  px(-17+lean,-39,5,34,'#010201');px(12+lean,-41,5,36,'#010201');
  px(-11,-2,6,31,'#010201');px(4,0,6,32,'#010201');
  if(flick>.12){ctx.fillStyle='#dad0b4';ctx.fillRect(-5,-56,3,2);ctx.fillRect(3,-56,3,2);}
  if(flick<-.72){ctx.fillStyle='rgba(165,22,30,.75)';ctx.fillRect(-6,-56,3,2);ctx.fillRect(3,-56,3,2);}
  if(p.kind==='copy'&&flick>.45){ctx.fillStyle='#050605';ctx.fillRect(-7,-31,14,2);ctx.fillRect(-4,-28,8,2);}
  ctx.restore();
}
function updateFearDirector(dt){
  if(!state.running||state.paused||state.gameOver||state.prologueStage!=='swamp')return;
  updateTrailPhantom(dt);
  state.apparitionTimer=Math.max(0,state.apparitionTimer-dt);
  if(Array.isArray(state.storyScareQueue)&&state.storyScareQueue.length){
    const queued=state.storyScareQueue[0];
    queued.delay-=dt;
    if(queued.delay<=0&&state.personalScareTimer<=0&&state.personalScareCooldown<=0){
      state.storyScareQueue.shift();
      if(state.options.personalScares)triggerPersonalScare(queued.kind);
    }
  }
  const presence=state.indoorPresence;
  if(state.floor==='inside'&&state.room&&monster&&monster.active&&presence){
    presence.phase+=dt;
    presence.timer=Math.max(0,presence.timer-dt);
    presence.cooldown=Math.max(-4,presence.cooldown-dt);
    if(presence.arming>0){
      presence.arming=Math.max(0,presence.arming-dt);
      if(presence.arming===0){
        let px=player.x,py=player.y,placed=false;
        for(let attempt=0;attempt<12;attempt++){
          const angle=Math.random()*Math.PI*2;
          const radius=175+Math.random()*185;
          const tx=clamp(player.x+Math.cos(angle)*radius,52,state.room.w-52);
          const ty=clamp(player.y+Math.sin(angle)*radius,52,state.room.h-52);
          if(dist(player.x,player.y,tx,ty)>150){px=tx;py=ty;placed=true;break;}
        }
        if(!placed){px=player.x<state.room.w/2?state.room.w-72:72;py=player.y<state.room.h/2?state.room.h-72:72;}
        presence.x=px;presence.y=py;presence.timer=1.1+Math.random()*1.15;presence.phase=Math.random()*15;presence.appearances=(presence.appearances||0)+1;
        state.intensity=Math.max(state.intensity,.82);state.screenShake=Math.max(state.screenShake,.13);state.noise=Math.max(state.noise,.18);
        sound('radio');voiceNoise(choose(['left','right']),.18);
        if(state.options.voiceWhispers)speakWhisper(choose(['It moved when you looked away.','I am standing somewhere else now.','Do not count the shadows.','You saw me leave. You did not see me arrive.','I can wait in every corner at once.']),choose(['left','right']));
        if(presence.appearances%2===0)toast('THE SMILER IS IN A DIFFERENT PART OF THE ROOM.',2.1);
      }
    }else if(presence.timer<=0&&presence.cooldown<=0){
      presence.cooldown=12+Math.random()*13;
      presence.arming=.45+Math.random()*.9;
      state.intensity=Math.max(state.intensity,.67);
      sound('radio');tone(54,.24,'triangle',.055,-24);
      voiceNoise(choose(['left','right']),.13);
      if(Math.random()<.38)toast('THE FOOTSTEPS STOP. THE ROOM HAS GONE QUIET.',2.0);
    }
  }

  state.apparitionCooldown=Math.max(0,state.apparitionCooldown-dt);
  const rescued=survivors.filter(s=>s.found||s.following||s.delivered).length;
  if(rescued>=1&&!state.horrorEventFlags.firstRescue){
    state.horrorEventFlags.firstRescue=true;
    state.intensity=Math.max(state.intensity,.68);
    state.screenShake=Math.max(state.screenShake,.18);
    voiceNoise(choose(['left','right']),.11);
    triggerWhisper('That one was already dead when you found them.','right','UNKNOWN OFFICER');
    toast('RADIO: YOUR PARTNER CLAIMS THE BODYCAM SHOWS AN EMPTY ROOM.',4.0);
  }
  if(rescued>=2&&!state.horrorEventFlags.bothRescued){
    state.horrorEventFlags.bothRescued=true;
    queueStoryScare('contact','bothRescueTruth',.65);
    state.intensity=1;
    state.screenShake=Math.max(state.screenShake,.42);
    sound('scare');
    triggerWhisper('You brought them back to the wrong place.','left','VOICE FROM THE PATROL CAR');
    toast('TWO RESCUE SIGNALS CONFIRMED. A THIRD SIGNAL IS INSIDE YOUR RADIO.',4.5);
    state.apparitionCooldown=3.5;
  }
  if(state.elapsed>30&&state.apparitionCooldown<=0&&monster&&monster.active&&!monster.hidden&&state.floor==='outside'){
    const a=player.angle+Math.PI+choose([-1,1])*(.42+Math.random()*.72);
    const d=260+Math.random()*210;
    state.apparitionX=clamp(player.x+Math.cos(a)*d,36,WORLD.w-36);
    state.apparitionY=clamp(player.y+Math.sin(a)*d,36,WORLD.h-36);
    state.apparitionTimer=.58+Math.random()*.58;
    state.apparitionCooldown=13+Math.random()*13;
    state.intensity=Math.max(state.intensity,.42);
    if(state.voiceCooldown<=0)triggerWhisper(choose(['Don’t look at the edge of the light.','It’s been standing behind you for a while.','You saw that. Do not tell dispatch.','It borrowed your partner’s voice.']),choose(['left','right']),'SHADOW AT THE EDGE OF THE BEAM');
    if(Math.random()<.45)sound('radio');
  }
  if(monster&&monster.active&&!monster.hidden){
    const d=dist(player.x,player.y,monster.x,monster.y);
    if(d<225){state.intensity=Math.max(state.intensity,.64);}
    if(d<165&&state.elapsed-(state.horrorEventFlags.lastHeartbeat||0)>(state.huntActive?.9:3.1)){state.horrorEventFlags.lastHeartbeat=state.elapsed;tone(state.huntActive?50:43,.32,'sine',state.huntActive?.12:.07,-12);tone(state.huntActive?39:38,.22,'triangle',state.huntActive?.085:.05,-7);}
    if(d<105&&state.voiceCooldown<=0)triggerWhisper(choose(['Don’t blink.','I’m close enough to hear your heartbeat.','Your light is getting tired.','It can see the inside of your eyelids.']),choose(['left','right']),'THE SMILER');
  }
}
function drawFalseFigure(){
  if(state.apparitionTimer<=0||state.floor!=='outside'||state.prologueStage!=='swamp')return;
  const angle=angleTo(player.x,player.y,state.apparitionX,state.apparitionY);
  const edgeX=W*.5+Math.cos(angle)*W*.34;
  const edgeY=H*.5+Math.sin(angle)*H*.30;
  const x=clamp(edgeX,24,W-24);
  const y=clamp(edgeY,74,H-35);
  const fade=Math.min(1,state.apparitionTimer*2.6);
  ctx.save();ctx.globalAlpha=fade*.92;
  const flick=Math.sin(state.elapsed*37)*2;
  ctx.fillStyle='#020403';
  ctx.fillRect(x-11,y-38+flick,22,43);
  ctx.fillRect(x-8,y-51+flick,16,18);
  ctx.fillRect(x-17,y-28,6,27);
  ctx.fillRect(x+11,y-28,6,27);
  ctx.fillRect(x-8,y+4,6,17);
  ctx.fillRect(x+2,y+4,6,17);
  if(Math.sin(state.elapsed*59)>.2){
    ctx.fillStyle='#c4423d';
    ctx.fillRect(x-5,y-44,3,2);
    ctx.fillRect(x+3,y-44,3,2);
  }
  ctx.fillStyle='#030403';
  ctx.fillRect(x-2,y+20,4,10);
  ctx.fillRect(x-8,y+28,7,2);
  ctx.fillRect(x+3,y+28,7,2);
  if(Math.sin(state.elapsed*21.7)>.7){
    ctx.fillStyle='rgba(178,29,33,'+(0.34+fade*.42)+')';
    ctx.fillRect(x-5,y-44,3,2);
    ctx.fillRect(x+3,y-44,3,2);
  }
  ctx.restore();
}
function updateVanishingItems(dt){
  if(!state.running||state.paused||state.gameOver||state.prologueStage!=='swamp'||state.missingCount>=5)return;
  state.missingTimer-=dt;
  if(state.missingTimer>0)return;
  state.missingTimer=27+Math.random()*14;
  const available=[];
  for(const item of objects){
    if(!item.found&&!item.missing&&['loot','evidence'].includes(item.type))available.push(item);
  }
  if(state.floor==='inside'&&state.room){
    for(const item of state.room.items){
      if(!item.found&&!item.missing&&['loot','note'].includes(item.type))available.push(item);
    }
  }
  if(!available.length)return;
  const loot=available.filter(item=>item.type==='loot'&&item.loot!=='keys');
  const uncollectedWorldEvidence=objects.filter(item=>item.type==='evidence'&&!item.found&&!item.missing).length;
  const notes=available.filter(item=>item.type==='note');
  const safeEvidence=available.filter(item=>item.type==='evidence'&&uncollectedWorldEvidence>4);
  const pool=loot.length?loot:notes.length?notes:safeEvidence;
  if(!pool.length){state.missingTimer=18;return;}
  const item=choose(pool);
  item.missing=true;
  if(item.id&&!state.missingIds.includes(item.id))state.missingIds.push(item.id);
  if(state.floor==='inside'&&item.id){state.roomItemStates=state.roomItemStates||{};state.roomItemStates[item.id]={found:false,missing:true};}
  state.missingCount++;
  const detail='You remember seeing '+item.name+' here. It is gone now. No footsteps lead away from the spot.';
  state.disappearanceLog.push({title:'FIELD NOTE '+String(state.missingCount).padStart(2,'0')+' · '+String(item.name).toUpperCase(),detail});
  caseRecords.push({id:'absence-'+state.missingCount,name:'Disappearance: '+item.name,detail,analysis:'The disappearance happened without a broken lock, disturbed dust, or a visible trail. The object was present during the previous sweep. The scene may be changing when you are not looking.',kind:'absence',studied:false});
  state.intensity=Math.min(1,state.intensity+.12);
  state.screenShake=Math.max(state.screenShake,.16);
  sound('radio');
  if(state.options.voiceWhispers&&Math.random()<.65)triggerWhisper(choose(['You should have taken it sooner.','There was something on the table a moment ago.','You keep losing things. Soon you will lose the way out.','Count the objects again. Slowly.']),choose(['left','right']),'VOICE FROM THE EMPTY ROOM');
  toast(choose(['SOMETHING HAS GONE MISSING: ','YOU LOOK AWAY. WHEN YOU LOOK BACK, IT IS GONE: ','FIELD INVENTORY DOES NOT MATCH: '])+item.name.toUpperCase(),4);
  updateObjectives();
}
function beginAdaptiveHunt(kind){
  if(state.huntActive||state.huntsTriggered>=5||state.elapsed<25)return false;
  state.huntsTriggered++;
  state.huntActive=true;
  state.huntKind=kind||'THE SMILER FOUND YOUR ROUTE';
  state.huntTimer=18.5+Math.random()*5.5+Math.max(0,state.huntsTriggered-3)*1.7;
  state.huntWarning=Math.max(1.75,2.65-Math.max(0,state.huntsTriggered-2)*.18);
  state.intensity=1;
  state.noise=Math.max(state.noise,.68);
  state.flashlightFlickerTimer=Math.max(state.flashlightFlickerTimer||0,1.2+Math.random()*.9);
  state.screenShake=Math.max(state.screenShake,.24);
  state.realityPulseTimer=0;
  $('realityPulse').classList.remove('active');
  state.apparitionX=clamp(player.x+Math.cos((player.angle||0)+Math.PI)*320,30,WORLD.w-30);
  state.apparitionY=clamp(player.y+Math.sin((player.angle||0)+Math.PI)*260,30,WORLD.h-30);
  state.apparitionTimer=1.05;
  activateMonster();
  if(state.floor==='outside'&&monster){
    let tx=player.x,ty=player.y,placed=false;
    for(let i=0;i<18;i++){
      const a=(player.angle||0)+Math.PI+(Math.random()-.5)*1.9;
      const r=178+Math.random()*115;
      const x=clamp(player.x+Math.cos(a)*r,64,WORLD.w-64);
      const y=clamp(player.y+Math.sin(a)*r,64,WORLD.h-64);
      if(!blockedAt(x,y,monster.r+4)&&dist(player.x,player.y,x,y)>145){tx=x;ty=y;placed=true;break;}
    }
    if(!placed){tx=clamp(player.x+Math.cos(player.angle+Math.PI)*195,64,WORLD.w-64);ty=clamp(player.y+Math.sin(player.angle+Math.PI)*195,64,WORLD.h-64);}
    monster.x=tx;monster.y=ty;monster.hidden=false;monster.vanishTimer=0;monster.stun=0;monster.attack=Math.max(monster.attack,.6);monster.activeTime=0;monster.vanishCooldown=state.huntActive?3.4:6.5;
  }else if(state.floor==='inside'&&state.room){
    const apparition=state.indoorPresence;
    apparition.x=clamp(state.room.exit.x+(Math.random()-.5)*150,55,state.room.w-55);
    apparition.y=clamp(state.room.exit.y-135-Math.random()*120,55,state.room.h-55);
    apparition.timer=2.4;apparition.arming=0;apparition.cooldown=3.2;apparition.phase=Math.random()*15;
  }
  const banner=$('huntBanner');
  document.body.classList.add('hunting');
  hideToast();
  banner.classList.add('active');
  $('huntBannerSub').textContent='MOVE NOW · HIDE ONLY BRIEFLY · THE HUNT LASTS '+Math.ceil(state.huntTimer)+' SECONDS';
  sound('scare');tone(36,.82,'sawtooth',.18,-22);tone(118,.24,'square',.08,-68);voiceNoise(choose(['left','right']),.2);
  if(state.options.voiceWhispers)speakWhisper(choose(['I waited until you were tired.','You make the same turn every time.','I found the place you think is safe.','Run if you want. I have been there already.','I do not need to follow you. I only need to know where you will stop.']),choose(['left','right']));
  addPartnerMessage(choose(['DON’T FOLLOW THE VOICE. SOMETHING IS MOVING ON YOUR FEED.','I can see it behind you. That is impossible. The camera is facing you.','RUN TO COVER. The shape on the feed is closer than the map shows.']),'incoming');
  if(kind==='RADIO BAIT')toast('THE COORDINATES WERE A TRAP.',1.8);
  return true;
}
function beginRadioBreach(){
  if(state.radioIncidentActive||state.radioIncidentCount>=2||state.screen!=='game')return false;
  state.radioIncidentActive=true;
  state.radioIncidentTimer=10.5;
  const n=state.radioIncidentCount+1;
  $('radioBreachCount').textContent='TRANSMISSION '+String(n).padStart(2,'0')+' / 02';
  $('radioBreachTitle').textContent=n===1?'YOUR PARTNER IS CALLING FROM INSIDE THE HOUSE':'THE BODYCAM IS TRANSMITTING FROM TOMORROW';
  $('radioBreachCopy').textContent=n===1?'The secure channel opens without a keypress. The voice uses your partner’s pauses and breathing, but the dispatch log says they never keyed the mic. Keep moving while you decide.':'The voice on the recording describes a choice you have not made yet. It knows the exact location of the next thing you will lose.';
  $('radioBreachTranscript').textContent=n===1?'PARTNER: “I need you to come to the marker. I’m hurt.”\nDISPATCH: “No second officer is assigned.”\nPARTNER: “Why did you let me in?”':'BODYCAM: “You are about to follow the coordinates.”\nPARTNER: “Do not follow them.”\nBODYCAM: “You already did.”';
  $('radioBreachTimer').textContent='AUTOMATIC RESPONSE IN 11 SECONDS · ANSWER WHILE YOU MOVE';
  $('radioBreachPanel').classList.remove('hidden');
  sound('radio');tone(71,.55,'triangle',.085,-29);voiceNoise(choose(['left','right']),.17);
  return true;
}
function resolveRadioBreach(choice){
  if(!state.radioIncidentActive)return;
  state.radioIncidentActive=false;
  state.radioIncidentTimer=0;
  state.radioIncidentCount++;
  state.adaptiveHorror.radioChoices++;
  $('radioBreachPanel').classList.add('hidden');
  state.paused=false;
  state.lastFrame=performance.now();
  if(choice==='verify'){
    state.adaptiveHorror.verifiedCalls++;
    state.noise=Math.max(0,state.noise-.48);
    flashlightBattery=Math.min(100,flashlightBattery+12);
    state.intensity=Math.max(.18,state.intensity-.22);
    state.threatTier=Math.max(0,(state.threatTier||0)-1);
    const id='verified-transmission-'+state.radioIncidentCount;
    if(!caseRecords.some(r=>r.id===id))caseRecords.push({id,name:'Verified false dispatch transmission '+state.radioIncidentCount,detail:'The caller used a valid voiceprint but failed a response check contained in the studied dispatch record.',analysis:'The message was assembled from copied speech fragments. The pauses and breathing are cut from different recordings. It was meant to make the officer move before thinking.',kind:'anomaly',studied:true});
    toast('CALL SIGN VERIFIED. THE VOICE DOES NOT KNOW THE RESPONSE. YOU HAVE BOUGHT A LITTLE TIME.',3.5);
    addPartnerMessage('Good. I did not send that transmission. Someone has copied the pauses in my voice.','incoming');
    tone(385,.22,'sine',.055,80);
  }else if(choice==='follow'){
    state.noise=1;state.intensity=1;state.threatTier=Math.min(7,(state.threatTier||0)+1);
    state.falseSignal={active:true,x:clamp(player.x+choose([-1,1])*(330+Math.random()*180),80,WORLD.w-80),y:clamp(player.y+choose([-1,1])*(230+Math.random()*170),80,WORLD.h-80),timer:22,triggered:false};
    if(!caseRecords.some(r=>r.id==='false-coordinate-trap'))caseRecords.push({id:'false-coordinate-trap',name:'False dispatch coordinates',detail:'A radio call directed you toward a signal that has no authorized transmitter.',analysis:'The signal was emitted from a location that moves between readings. It is not a safe extraction point. Approaching it may trigger a close encounter.',kind:'anomaly',studied:false});
    if(!state.huntActive)beginAdaptiveHunt('RADIO BAIT');
    toast('COORDINATES ACCEPTED. THE SIGNAL IS MOVING TOWARD YOU.',3.8);
    addPartnerMessage('That marker is not mine. If you can see it, do not trust the green light.','incoming');
  }else{
    state.noise=Math.max(0,state.noise-.72);
    state.radioSilenceUntil=state.elapsed+14;
    state.helpCooldown=Math.max(state.helpCooldown,13);
    state.intensity=Math.max(state.intensity,.34);
    toast('CHANNEL CUT. YOU ARE QUIETER, BUT ALONE FOR 14 SECONDS.',3.2);
    addPartnerMessage('…','incoming');
  }
  state.adaptiveHorror.sprintExposure=Math.max(0,state.adaptiveHorror.sprintExposure-3);
  updateObjectives();updateHUD();
}
function updateAdaptiveHorror(dt){
  if(!state.running||state.paused||state.gameOver||state.prologueStage!=='swamp')return false;
  if(state.radioIncidentActive){
    state.radioIncidentTimer=Math.max(0,state.radioIncidentTimer-dt);
    const timer=$('radioBreachTimer');
    if(timer)timer.textContent='AUTOMATIC RESPONSE IN '+Math.ceil(state.radioIncidentTimer)+' SECONDS · ANSWER WHILE YOU MOVE';
    if(state.radioIncidentTimer<=0){resolveRadioBreach('follow');return true;}
  }
  const a=state.adaptiveHorror;
  a.flashlightExposure=flashlight?Math.min(150,a.flashlightExposure+dt):Math.max(0,a.flashlightExposure-dt*.26);
  state.realityPulseCooldown=Math.max(0,state.realityPulseCooldown-dt);
  state.realityPulseTimer=Math.max(0,state.realityPulseTimer-dt);
  $('realityPulse').classList.toggle('active',state.realityPulseTimer>0);
  if(state.falseSignal.active){
    state.falseSignal.timer-=dt;
    if(state.floor==='outside'&&!state.falseSignal.triggered&&dist(player.x,player.y,state.falseSignal.x,state.falseSignal.y)<88){
      state.falseSignal.triggered=true;state.falseSignal.active=false;state.noise=1;state.intensity=1;state.screenShake=Math.max(state.screenShake,.32);
      spawnCrawlerWave(3,155,105,3);
      if(monster){monster.hidden=false;monster.x=clamp(player.x+Math.cos(player.angle+Math.PI)*155,55,WORLD.w-55);monster.y=clamp(player.y+Math.sin(player.angle+Math.PI)*155,55,WORLD.h-55);monster.attack=Math.max(monster.attack,.65);}
      triggerWhisper('You came all this way because I asked you to.','behind','FALSE DISPATCH');
      toast('THE BEACON WAS NEVER THERE. SOMETHING RISES OUT OF THE GROUND.',4.0);
    }else if(state.falseSignal.timer<=0){state.falseSignal.active=false;toast('THE FALSE SIGNAL HAS GONE QUIET. THE REAL BEACON IS STILL WHERE IT WAS.',2.7);}
  }
  if(state.huntActive){
    state.huntTimer-=dt;
    state.huntWarning=Math.max(0,state.huntWarning-dt);
    const banner=$('huntBanner');
    banner.classList.add('active');
    $('huntBannerSub').textContent=state.huntWarning>0?'IT IS CHANGING POSITION · '+state.huntWarning.toFixed(1)+'s':'SURVIVE '+Math.max(0,Math.ceil(state.huntTimer))+'s · KEEP MOVING, THEN BREAK LINE OF SIGHT';
    if(state.floor==='inside'&&state.room&&state.indoorPresence){
      const p=state.indoorPresence;
      p.timer=Math.max(p.timer,.75);
      if(state.huntWarning<=0){
        const ang=angleTo(p.x,p.y,player.x,player.y);
        const pace=32+(state.threatTier||0)*2.2;
        const nx=p.x+Math.cos(ang)*pace*dt,ny=p.y+Math.sin(ang)*pace*dt;
        if(!insideBlocked(nx,p.y))p.x=nx;
        if(!insideBlocked(p.x,ny))p.y=ny;
        p.phase+=dt*5;
      }
    }
    if(state.huntTimer<=0){
      state.huntActive=false;state.huntsSurvived++;state.nextHuntAt=state.elapsed+31+Math.random()*22;
      document.body.classList.remove('hunting');
      $('huntBanner').classList.remove('active');
      flashlightBattery=Math.min(100,flashlightBattery+5);
      const id='survived-hunt-'+state.huntsSurvived;
      if(!caseRecords.some(r=>r.id===id))caseRecords.push({id,name:'Hunt survival recording '+state.huntsSurvived,detail:'The bodycam continued recording while the officer was being hunted.',analysis:'The creature changed direction whenever the officer changed pace. Its footsteps were sometimes heard ahead of the officer rather than behind. It appears to predict routes instead of following them.',kind:'anomaly',studied:false});
      state.intensity=Math.max(.45,state.intensity-.15);state.noise=Math.max(.15,state.noise-.25);
      toast('YOU SURVIVED THE HUNT. THE FOOTSTEPS STOP — NOT FADE, STOP.',3.8);
      triggerWhisper('I let you finish that breath. Do not mistake it for mercy.','center','BODYCAM AUDIO');
      updateObjectives();updateHUD();
    }
  }else{
    document.body.classList.remove('hunting');
    $('huntBanner').classList.remove('active');
    const rescued=survivors.filter(s=>s.found||s.following||s.delivered).length;
    const clueCount=collectedClueCount();
    const eligible=state.elapsed>=state.nextHuntAt&&monster&&monster.active&&state.huntsTriggered<5;
    if(eligible){
      const n=state.huntsTriggered;
      const ready=n===0||(n===1&&(clueCount>=3||a.sprintExposure>11||state.missingCount>=1))||(n===2&&(rescued>=1||state.stationComplete||studyCount()>=4))||(n===3&&(clueCount>=5||state.elapsed>=180||state.missingCount>=2))||(n===4&&(rescued>=1&&clueCount>=5||state.elapsed>=250));
      const huntNames=['FIRST CONTACT','THE LEARNED ROUTE','THE LAST SEARCH','NO SAFE ROOM','THE THING THAT WAITS'];
      if(ready)beginAdaptiveHunt(huntNames[n]||'THE THING THAT WAITS');
    }
  }
  if(!state.horrorEventFlags.nextPhantomAudioAt)state.horrorEventFlags.nextPhantomAudioAt=state.elapsed+16+Math.random()*12;
  if(state.elapsed>=state.horrorEventFlags.nextPhantomAudioAt&&!state.radioIncidentActive&&state.personalScareTimer<=0&&state.huntsTriggered>0){
    state.horrorEventFlags.nextPhantomAudioAt=state.elapsed+22+Math.random()*24;
    const side=choose(['left','right']);
    if(state.floor==='inside'){
      sound('door');tone(34,.5,'sawtooth',.05,-24);
      if(state.options.voiceWhispers&&state.voiceCooldown<=0)triggerWhisper(choose(['Someone just tried the handle from the other side.','There are footsteps in the ceiling. They stopped over you.','Someone turned the handle while you were listening to the radio.','Your partner stopped breathing for four seconds. Ask them why.']),side,'UNRECORDED AUDIO');
    }else{
      sound('step');voiceNoise(side,.075);
      if(state.options.voiceWhispers&&state.voiceCooldown<=0)triggerWhisper(choose(['It is walking at your speed, one tree away.','The steps are ahead of you. You are still moving forward.','Something is running beside you without bending the grass.','Do not follow the breathing. It is leading you back.']),side,'FIELD MICROPHONE');
    }
    state.intensity=Math.max(state.intensity,.62);
  }
  if(a.sprintExposure>20&&!state.horrorEventFlags.runHabit){
    state.horrorEventFlags.runHabit=true;state.nextHuntAt=Math.min(state.nextHuntAt,state.elapsed+5);
    triggerWhisper('You always run when the sound is behind you. I will start making it sound like it is ahead.','left','MOVEMENT PROFILE');
    toast('IT HAS LEARNED YOUR RUNNING PACE.',3.1);
  }
  if(a.hideCount>=3&&!state.horrorEventFlags.hideHabit){
    state.horrorEventFlags.hideHabit=true;state.nextHuntAt=Math.min(state.nextHuntAt,state.elapsed+8);
    triggerWhisper('Three hiding places. Three slow heartbeats. I can count through walls.','right','ROOM ACOUSTICS');
    toast('YOUR HIDING HABIT HAS BEEN LOGGED.',3.0);
  }
  if(state.shots>=3&&!state.horrorEventFlags.gunfireHabit){
    state.horrorEventFlags.gunfireHabit=true;state.shotsAttracted=true;
    if(state.floor==='outside')spawnCrawlerWave(2,180,101,3);
    triggerWhisper('Every shot makes a map of where you are. Thank you.','center','ACOUSTIC TRACKING');
    toast('GUNFIRE ATTRACTED MOVEMENT IN THE TREES.',3.3);
  }
  if(a.flashlightExposure>38&&!state.horrorEventFlags.lightHabit){
    state.horrorEventFlags.lightHabit=true;state.flashlightFlickerTimer=Math.max(state.flashlightFlickerTimer||0,2.1);
    state.nextHuntAt=Math.min(state.nextHuntAt,state.elapsed+9);
    triggerWhisper('You point the light at what you fear. I learned to wait just outside it.','left','FLASHLIGHT PATTERN');
    toast('THE SMILER HAS LEARNED THE EDGE OF YOUR BEAM.',3.2);
  }
  if(!state.horrorEventFlags.nextStalkingBeat)state.horrorEventFlags.nextStalkingBeat=state.elapsed+12+Math.random()*10;
  if(state.elapsed>=state.horrorEventFlags.nextStalkingBeat&&!state.huntActive&&!state.radioIncidentActive&&state.personalScareTimer<=0&&state.floor==='inside'&&state.room){
    state.horrorEventFlags.nextStalkingBeat=state.elapsed+18+Math.random()*22;
    const side=choose(['left','right']);
    sound('door');tone(39,.48,'sawtooth',.045,-28);voiceNoise(side,.11);
    state.intensity=Math.max(state.intensity,.58);
    if(state.screenShake<.08)state.screenShake=.08;
    if(state.options.voiceWhispers&&state.voiceCooldown<=0)triggerWhisper(choose(['Someone just tried the handle from the other side.','There was a second set of footsteps in your last recording.','The room is quiet because it is listening.','Your partner stopped breathing for four seconds. Ask them why.']),side,'ACOUSTIC INCIDENT');
  }
  const radioReady=state.radioIncidentCount===0?state.elapsed>=state.nextRadioIncidentAt&&collectedClueCount()>=1&&studyCount()>=1:state.elapsed>=state.nextRadioIncidentAt&&(state.stationComplete||studyCount()>=4||state.rescued>=1);
  if(!state.radioIncidentActive&&!state.huntActive&&state.radioIncidentCount<2&&radioReady&&state.screen==='game'){
    state.nextRadioIncidentAt=state.elapsed+58+Math.random()*22;
    return beginRadioBreach();
  }
  if(state.radioSilenceUntil>state.elapsed){
    const box=$('partnerChat');if(box)box.classList.add('radio-silenced');
  }else{
    const box=$('partnerChat');if(box)box.classList.remove('radio-silenced');
  }
  if(state.floor==='inside'&&state.room&&state.elapsed>65&&state.realityPulseCooldown<=0&&state.exploredRoomIds.length>=2&&Math.random()<dt*.018){
    state.realityPulseCooldown=23+Math.random()*18;state.realityPulseTimer=.35+Math.random()*.75;state.realityPulseCount++;
    state.screenShake=Math.max(state.screenShake,.12);sound('radio');voiceNoise(choose(['left','right']),.12);
    if(state.realityPulseCount%2===0){state.indoorEcho.active=true;state.indoorEcho.timer=Math.max(state.indoorEcho.timer,1.8);state.indoorEcho.cooldown=Math.min(state.indoorEcho.cooldown,7);}
    if(state.options.voiceWhispers)triggerWhisper(choose(['You already went through this room.','The door is behind you. Why is the sound ahead?','Something moved in the room while the picture was black.','Count the corners again.']),choose(['left','right']),'ROOM MEMORY ERROR');
  }
  return false;
}
function drawFalseSignal(){
  if(!state.falseSignal.active||state.floor!=='outside')return;
  const x=state.falseSignal.x-camera.x+shakeX,y=state.falseSignal.y-camera.y+shakeY;
  if(x<-70||y<-70||x>W+70||y>H+70)return;
  const pulse=.5+.5*Math.sin(state.elapsed*8.5);
  ctx.save();ctx.globalCompositeOperation='screen';ctx.globalAlpha=.72;
  const g=ctx.createRadialGradient(x,y,0,x,y,35+18*pulse);g.addColorStop(0,'rgba(132,221,178,.5)');g.addColorStop(1,'rgba(80,190,139,0)');ctx.fillStyle=g;ctx.fillRect(x-60,y-60,120,120);ctx.restore();
  ctx.save();ctx.strokeStyle='rgba(135,236,179,'+(.42+.36*pulse)+')';ctx.lineWidth=1.4;ctx.beginPath();ctx.arc(x,y,9+5*pulse,0,Math.PI*2);ctx.stroke();ctx.fillStyle='#a7f1cb';ctx.fillRect(x-2,y-2,5,5);ctx.fillStyle='#c8ead2';ctx.font='bold 8px monospace';ctx.textAlign='center';ctx.fillText('DISPATCH SIGNAL',x,y-17);ctx.restore();
}
function drawRealityText(){
  if(state.realityPulseTimer<=0||state.huntActive)return;
  const strength=Math.min(1,state.realityPulseTimer*2.1);
  ctx.save();ctx.globalAlpha=strength*.27;ctx.fillStyle='#4e0810';ctx.font='bold '+Math.max(13,Math.min(24,W*.028))+'px monospace';ctx.textAlign='center';ctx.fillText('YOU HAVE ALREADY BEEN HERE',W*.5,H*.20);ctx.restore();
}
function update(dt){
  if(state.prologueStage!=='swamp'){updatePrologue(dt);return;}
  state.sceneFade=Math.max(0,state.sceneFade-dt*1.7);
  updatePersonalScare(dt);
  state.elapsed+=dt;
  updateSurvivalActions(dt);
  updateWhispers(dt);
  updateFearDirector(dt);
  updateThreatEscalation(dt);
  if(updateAdaptiveHorror(dt))return;
  state.missionClock+=dt;
  updatePartnerChat();
  if(state.horrorBeat===0&&state.elapsed>6.5){state.horrorBeat=1;sound('radio');toast('RADIO: “Officer… I can see you at the tree line.” DISPATCH DENIES SENDING THAT TRANSMISSION.',4.2);state.intensity=.78;state.screenShake=.19;triggerWhisper('Do not use your own voice to answer dispatch.','right','UNKNOWN OFFICER');}
  if(state.horrorBeat===1&&state.elapsed>15.5){state.horrorBeat=2;activateMonster();toast('SOMETHING BETWEEN THE TREES JUST MOVED. IT IS CLOSER THAN THE MAP SAYS.',3.4);}
  if(state.elapsed>27&&!state.horrorEventFlags.thirdFootstep){state.horrorEventFlags.thirdFootstep=true;sound('door');voiceNoise('behind',.13);toast('FOOTSTEPS: LEFT, RIGHT, LEFT, RIGHT… THEN A THIRD STEP BESIDE YOURS.',3.2);if(state.options.voiceWhispers)triggerWhisper('Do not slow down to count them.','behind','FOOTSTEPS / CHANNEL UNKNOWN');}
  growlTimer-=dt;
  shootTimer=Math.max(0,shootTimer-dt);
  reloadTimer=Math.max(0,reloadTimer-dt);
  interactCooldown=Math.max(0,interactCooldown-dt);
  damageCooldown=Math.max(0,damageCooldown-dt);
  if(reloadTimer===0&&reloadTimer!==-1&&ammo<6&&reserve>0&&state.reloadActive){
    const need=6-ammo;
    const take=Math.min(need,reserve);
    ammo+=take;
    reserve-=take;
    state.reloadActive=false;
    updateHUD();
    toast('MAGAZINE READY.',1.0);
  }
  if(reloadTimer===0&&ammo<6&&reserve>0&&!state.reloadActive)state.reloadActive=false;
  if(keys.r&&reloadTimer<=0&&!state.reloadActive){
    state.reloadActive=true;
    reloadWeapon();
    keys.r=false;
  }
  if(state.hideSpotActive)player.hidden=true;
  else if(state.floor==='outside'){
    const onReed=treeNear(player.x,player.y,25,25);
    player.hidden=onReed&&!keys.shift&&state.noise<.2;
  }else player.hidden=false;
  movePlayer(dt);
  updateIndoorEcho(dt);
  updateOutdoorMemoryEcho(dt);
  updateNightmareAtmosphere(dt);
  updateHauntingDirector(dt);
  updateSurvivors(dt);
  state.exitHintCooldown=Math.max(0,(state.exitHintCooldown||0)-dt);
  updateVanishingItems(dt);
  if(state.floor==='outside'){
    const extraction=objects.find(o=>o.type==='exit');
    const rescuedAtExit=survivors.filter(s=>s.found||s.following||s.delivered).length;
    const exitDistance=extraction?dist(player.x,player.y,extraction.x,extraction.y):Infinity;
    if(state.extractionStarted){
      if(exitDistance>165){
        state.extractionHold=0;
        state.extractionLastToast=0;
        if(!state.extractionWasOutside)toast('EXTRACTION ABORTED: RETURN TO THE BEACON. THE DEFENSE TIMER RESET.',3.1);
        state.extractionWasOutside=true;
      }else{
        state.extractionWasOutside=false;
        state.extractionHold+=dt;
        const held=Math.floor(state.extractionHold);
        if(held>=4&&!state.extractionWave1){
          state.extractionWave1=true;
          spawnCrawlerWave(2,185,98,3);
          toast('FIRST WAVE. THE BEACON IS DRAWING THEM TO YOU.',2.8);
          sound('roar');
        }
        if(held>=11&&!state.extractionWave2){
          state.extractionWave2=true;
          spawnCrawlerWave(3,225,108,3);
          toast('SECOND WAVE. THEY ARE LEARNING YOUR ROUTE.',3.1);
          sound('scare');
        }
        if(held>=18&&!state.extractionWave3){
          state.extractionWave3=true;
          spawnCrawlerWave(3,255,116,4);
          state.intensity=1;
          toast('THIRD WAVE. THE FIGURES ARE MOVING IN FORMATION.',3.4);
          sound('roar');
          triggerWhisper('They were never trying to stop you leaving. They were waiting for you to bring the others back.','center','DISPATCH // CHANNEL ZERO');
        }
        if(held>=25&&!state.extractionWave4){
          state.extractionWave4=true;
          spawnCrawlerWave(4,275,122,4);
          state.intensity=1;
          state.flashlightFlickerTimer=Math.max(state.flashlightFlickerTimer||0,1.4);
          toast('FOURTH WAVE. SOMETHING IS STANDING INSIDE THE BEACON.',3.6);
          sound('scare');
        }
        if(held>=27&&!state.finalManifestStarted){
          state.finalManifestStarted=true;
          if(monster){
            let tx=player.x+Math.cos(player.angle+Math.PI)*170,ty=player.y+Math.sin(player.angle+Math.PI)*170;
            for(let k=0;k<12&&blockedAt(tx,ty,monster.r+3);k++){const a=Math.random()*Math.PI*2;tx=clamp(player.x+Math.cos(a)*(155+k*5),55,WORLD.w-55);ty=clamp(player.y+Math.sin(a)*(155+k*5),55,WORLD.h-55);}
            monster.x=clamp(tx,55,WORLD.w-55);monster.y=clamp(ty,55,WORLD.h-55);monster.active=true;monster.hidden=false;monster.stun=0;monster.attack=.75;monster.reappearGlow=2.7;monster.activeTime=0;monster.vanishCooldown=12;monster.warpCooldown=5;
          }
          state.screenShake=Math.max(state.screenShake,.34);state.intensity=1;sound('roar');
          toast('THE LAST VOICE HAS ARRIVED AT THE BEACON. DO NOT LET IT TOUCH YOU.',4.0);
          if(state.options.voiceWhispers)triggerWhisper('You did not bring them home. You brought me to the door.','center','THE SMILER / FINAL RECORDING');
        }
        if(held>=state.extractionLastToast+5&&held<30){
          state.extractionLastToast=held;
          toast('EXTRACTION HOLD: '+(30-held)+' SECONDS REMAIN. STAY INSIDE THE BEACON RADIUS.',2.2);
        }
        if(state.extractionHold>=30){completeExtraction();return;}
      }
    }else if(extraction&&exitDistance<142){
      if(rescuedAtExit>=2&&investigationReady()&&state.keysFound&&state.exploredRoomIds.length>=5){
        if(state.exitHintCooldown<=0){toast('CASEWORK COMPLETE. PRESS E TO START THE 30-SECOND EXTRACTION DEFENSE.',3.0);state.exitHintCooldown=5;}
      }else if(state.exitHintCooldown<=0){
        const blocker=rescuedAtExit<2?'RESCUE BOTH PEOPLE ('+rescuedAtExit+'/2)':collectedClueCount()<6?'COLLECT SIX CLUES ('+collectedClueCount()+'/6)':studyCount()<6?'STUDY SIX CLUES IN CASE FILE [J] ('+studyCount()+'/6)':validCrossReferenceCount()<4?'PRODUCE FOUR DISTINCT CROSS-REFERENCE REPORTS ('+validCrossReferenceCount()+'/4)':state.caseTheory!=='mimic-timeline'?'SUBMIT A SUPPORTED CASE THEORY':!state.witnessInterviewed?'INTERVIEW SILAS VENN':state.witnessTrust<2?'GET A CORROBORATED WITNESS STATEMENT':!state.stationComplete?'SCREEN SIX VISITORS AT THE COUNTY POLICE STATION (FIVE CORRECT)':!state.keysFound?'RECOVER THE RELAY OVERRIDE KEY IN THE RADIO RELAY HUT':'SEARCH FIVE DIFFERENT BUILDINGS';
        toast('EXTRACTION LOCKED: '+blocker+'.',3.5);
        state.exitHintCooldown=5;
      }
    }
  }
  updateCrawlers(dt);
  updateMonster(dt);
  updateBullets(dt);
  updateWeather(dt);
  if(flashlight&&flashlightBattery>0){
    const nearThreat=monster&&monster.active&&dist(player.x,player.y,monster.x,monster.y)<370?0.34:0;
    const dangerDrain=1+Math.min(.7,state.elapsed/240)+state.missingCount*.045+nearThreat;
    flashlightBattery=Math.max(0,flashlightBattery-dt*(state.floor==='inside'?.56:.27)*dangerDrain);
    if(flashlightBattery<=0){flashlight=false;toast('FLASHLIGHT BATTERY EXHAUSTED.',2);}
  }
  if(state.floor==='outside'){
    camera.x=clamp(player.x-W/2,0,WORLD.w-W);
    camera.y=clamp(player.y-H/2,0,WORLD.h-H);
  }else if(state.room){
    camera.x=clamp(player.x-W/2,0,Math.max(0,state.room.w-W));
    camera.y=clamp(player.y-H/2,0,Math.max(0,state.room.h-H));
  }
  if(state.toastTimer>0){
    state.toastTimer-=dt;
    if(state.toastTimer<=0)hideToast();
  }
  state.radioTimer=Math.max(0,state.radioTimer-dt);
  state.hudClock=(state.hudClock||0)+dt;
  if(state.hudClock>=.075){state.hudClock=0;updateHUD();}
  if(pointer.down&&state.controlMode==='desktop')shoot();
}
function screenJitter(){
  if(state.options.shake&&state.screenShake>0){
    shakeX=(Math.random()-.5)*state.screenShake*22;
    shakeY=(Math.random()-.5)*state.screenShake*22;
  }else{
    shakeX=0;
    shakeY=0;
  }
}
function px(x,y,w,h,color){
  ctx.fillStyle=color;
  ctx.fillRect(Math.round(x),Math.round(y),Math.max(1,Math.round(w)),Math.max(1,Math.round(h)));
}
function worldPx(x,y,w,h,color){
  px(x-camera.x+shakeX,y-camera.y+shakeY,w,h,color);
}
function buildGroundCache(){
  const cache=document.createElement('canvas');
  cache.width=WORLD.w;
  cache.height=WORLD.h;
  const g=cache.getContext('2d',{alpha:false});
  g.fillStyle='#101a13';
  g.fillRect(0,0,WORLD.w,WORLD.h);
  for(let wy=0;wy<WORLD.h;wy+=TILE){
    for(let wx=0;wx<WORLD.w;wx+=TILE){
      const n=seeded(Math.floor(wx/TILE),Math.floor(wy/TILE));
      const color=n>.79?'#1b291b':n>.57?'#162319':n>.3?'#122018':'#101b14';
      g.fillStyle=color;
      g.fillRect(wx,wy,TILE,TILE);
      if(n>.91){
        g.fillStyle='#35412c';g.fillRect(wx+5,wy+7,9,2);
        g.fillStyle='#28382a';g.fillRect(wx+9,wy+11,4,2);
      }
      if(n<.06){
        g.fillStyle='#27352a';g.fillRect(wx+13,wy+20,8,4);
        g.fillStyle='#536151';g.fillRect(wx+16,wy+21,3,1);
      }
      if(n>.48&&n<.52){g.fillStyle='#202f22';g.fillRect(wx+23,wy+6,2,7);}
    }
  }
  groundCanvas=cache;
}
function drawGround(){
  px(0,0,W,H,'#101a13');
  if(!groundCanvas)buildGroundCache();
  const sx=clamp(camera.x,0,WORLD.w-1);
  const sy=clamp(camera.y,0,WORLD.h-1);
  const sw=Math.min(W,WORLD.w-sx);
  const sh=Math.min(H,WORLD.h-sy);
  if(sw>0&&sh>0)ctx.drawImage(groundCanvas,sx,sy,sw,sh,shakeX,shakeY,sw,sh);
}
function drawFootpaths(){
  ctx.save();
  ctx.lineCap='round';
  ctx.lineJoin='round';
  for(const route of FOOTPATHS){
    const first=route[0];
    ctx.beginPath();
    ctx.moveTo(first.x-camera.x+shakeX,first.y-camera.y+shakeY);
    for(let i=1;i<route.length;i++)ctx.lineTo(route[i].x-camera.x+shakeX,route[i].y-camera.y+shakeY);
    ctx.lineWidth=41;ctx.strokeStyle='#0b100a';ctx.stroke();
    ctx.lineWidth=32;ctx.strokeStyle='#252719';ctx.stroke();
    ctx.lineWidth=23;ctx.strokeStyle='#45412d';ctx.stroke();
    ctx.lineWidth=1.9;ctx.setLineDash([4,13]);ctx.strokeStyle='rgba(190,181,123,.56)';ctx.stroke();ctx.setLineDash([]);
  }
  for(let i=0;i<FOOTPATHS.length;i++){
    const route=FOOTPATHS[i];
    for(let j=0;j<route.length-1;j++){
      const a=route[j],b=route[j+1];
      const length=Math.hypot(b.x-a.x,b.y-a.y);
      const steps=Math.floor(length/88);
      for(let k=1;k<steps;k++){
        const wx=a.x+(b.x-a.x)*k/steps;
        const wy=a.y+(b.y-a.y)*k/steps;
        const sx=wx-camera.x+shakeX,sy=wy-camera.y+shakeY;
        if(sx<-10||sy<-10||sx>W+10||sy>H+10)continue;
        const pulse=.55+.12*Math.sin(i*5+j*3+k);
        ctx.globalAlpha=pulse;
        px(sx-2,sy-1,4,2,'#5a563a');
        if(k%2===0)px(sx+4,sy+3,2,1,'#777052');
      }
    }
  }
  ctx.restore();
}

function drawRoad(){
  ctx.save();
  ctx.lineCap='round';
  ctx.lineJoin='round';
  for(const p of roadNetworks()){
    ctx.beginPath();
    ctx.moveTo(p[0].x-camera.x+shakeX,p[0].y-camera.y+shakeY);
    for(let i=1;i<p.length;i++)ctx.lineTo(p[i].x-camera.x+shakeX,p[i].y-camera.y+shakeY);
    ctx.lineWidth=106;ctx.strokeStyle='#080d0a';ctx.stroke();
    ctx.lineWidth=96;ctx.strokeStyle='#272c24';ctx.stroke();
    ctx.lineWidth=84;ctx.strokeStyle='#353a30';ctx.stroke();
    ctx.lineWidth=78;ctx.strokeStyle='#414337';ctx.stroke();
    ctx.lineWidth=2;ctx.strokeStyle='#8f8567';ctx.setLineDash([18,23]);ctx.stroke();ctx.setLineDash([]);
  }
  ctx.restore();
  for(const detail of roadDetails){
    const x=detail.x-camera.x+shakeX;
    const y=detail.y-camera.y+shakeY;
    if(x>-40&&x<W+40&&y>-30&&y<H+30){
      px(x-10,y,22,3,'#222920');px(x-5,y+1,12,1,'#716c55');
      if(detail.i%3===0){px(x+7,y-4,2,8,'#343c2f');px(x+4,y-7,8,4,'#a6a085');}
    }
  }
}
function drawTree(t){
  const x=t.x-camera.x+shakeX;
  const y=t.y-camera.y+shakeY;
  const s=t.s;
  if(x<-85||y<-100||x>W+85||y>H+100)return;
  const palette=[
    ['#0a110c','#17271b','#263928','#39462e'],
    ['#0b130d','#1d2b1e','#2b3a29','#424b32'],
    ['#0e140e','#202b20','#30382a','#4a4b34']
  ][t.shade];
  const wind=Math.sin(state.elapsed*.75+t.phase)*1.7;
  px(x-13*s,y-4*s,26*s,12*s,'#080e0a');
  px(x-4*s,y-1*s,8*s,18*s,'#29281e');
  px(x-14*s+wind,y-20*s,28*s,20*s,palette[0]);
  px(x-12*s+wind,y-31*s,24*s,18*s,palette[1]);
  px(x-8*s+wind,y-41*s,16*s,15*s,palette[2]);
  px(x-4*s+wind,y-46*s,8*s,9*s,palette[3]);
  px(x-20*s+wind,y-13*s,10*s,12*s,palette[0]);
  px(x+10*s+wind,y-15*s,10*s,13*s,palette[0]);
  px(x-8*s+wind,y-28*s,5*s,4*s,'#405037');
  if(t.s>.95){
    px(x-2*s,y-37*s,3*s,2*s,'#566041');
    px(x+5*s,y-18*s,2*s,4*s,'#48523a');
  }
}
function drawReeds(){
  for(const r of reeds){
    const x=r.x-camera.x;
    const y=r.y-camera.y;
    if(x<-20||y<-25||x>W+20||y>H+20)continue;
    const swing=Math.sin(state.elapsed*2+r.phase)*2;
    px(x,y-r.h,2,r.h,'#263a28');
    px(x+swing-2,y-r.h+3,3,5,'#45523a');
    px(x+4,y-r.h*.7,2,r.h*.7,'#31442d');
  }
}
function drawPuddles(){
  for(const p of wetPatches){
    const x=p.x-camera.x;
    const y=p.y-camera.y;
    if(x<-80||y<-30||x>W+80||y>H+30)continue;
    px(x,y,p.w,p.h,'#0d1b18');
    px(x+3,y+2,p.w*.47,2,'#314c42');
    px(x+p.w*.63,y+p.h-3,p.w*.2,1,'#263e35');
  }
}
function drawBuilding(o){
  const x=o.x-camera.x+shakeX;
  const y=o.y-camera.y+shakeY;
  const w=o.w;
  const h=o.h;
  if(x<-w-50||y<-h-75||x>W+w+50||y>H+h+75)return;
  px(x-w/2-7,y-h/2+8,w+14,h+17,'#080e0a');
  px(x-w/2,y-h/2,w,h,'#494737');
  px(x-w/2+5,y-h/2+5,w-10,h-10,'#34382c');
  px(x-w/2-4,y-h/2-8,w+8,11,'#25291f');
  px(x-w/2-2,y-h/2-10,w+4,5,'#774336');
  px(x-w/2+5,y-h/2+11,w-10,3,'#595540');
  px(x-w/2+10,y-h/2+18,24,18,'#151d17');
  px(x-w/2+13,y-h/2+21,18,12,'#807c5c');
  px(x+w/2-35,y-h/2+18,24,18,'#131b15');
  px(x+w/2-32,y-h/2+21,18,12,'#736e52');
  px(x-12,y-h/2+h*.49,24,h*.38,'#0c100c');
  px(x-8,y-h/2+h*.49+5,16,h*.36,'#1c2119');
  px(x+4,y-h/2+h*.49+20,2,3,'#c2a46a');
  px(x-w/2-2,y+h/2-7,w+4,8,'#171d16');
  ctx.fillStyle='#d4c9a1';
  ctx.textAlign='center';
  ctx.font='9px monospace';
  ctx.fillText(o.name.toUpperCase(),x,y-h/2-17);
  if(Math.sin(state.elapsed*1.8+o.x)>-.3){
    px(x-w*.28,y-h/2+24,5,3,'#d4b979');
  }
  if(o.style==='motel'){
    px(x-w*.43,y-h/2+4,w*.86,10,'#673b32');px(x-w*.36,y-h/2+7,w*.72,3,'#b48e63');
    px(x-w*.12,y-h/2-27,w*.24,13,'#111a14');px(x-w*.105,y-h/2-24,w*.21,7,Math.sin(state.elapsed*7)>0?'#d45f4b':'#7d342d');
    ctx.fillStyle='#e0b876';ctx.font='bold 8px monospace';ctx.fillText('VACANCY',x,y-h/2-18);
  }
  if(o.style==='diner'){
    px(x-w*.48,y-h/2+5,w*.96,13,'#5d302a');px(x-w*.44,y-h/2+8,w*.88,4,'#c4a66c');
    for(let i=0;i<5;i++)px(x-w*.36+i*w*.18,y+h*.04,Math.max(6,w*.065),h*.12,'#a46d43');
    ctx.fillStyle='#e2c17b';ctx.font='bold 8px monospace';ctx.fillText('LAST STOP',x,y-h/2-17);
  }
  if(o.style==='clinic'){
    px(x-5,y-h/2-25,10,32,'#a8b6a3');px(x-16,y-h/2-15,32,10,'#a8b6a3');
    px(x-w*.34,y+h*.06,w*.19,h*.18,'#172c2c');px(x-w*.31,y+h*.09,w*.13,h*.12,'#688a81');
  }
  if(o.style==='depot'||o.style==='warehouse'){
    px(x-w*.34,y-h/2+18,w*.68,h*.44,'#171e18');px(x-w*.29,y-h/2+23,w*.58,h*.35,'#29362c');
    for(let i=0;i<5;i++)px(x-w*.26+i*w*.105,y-h/2+23,2,h*.35,'#4e5947');
    px(x-w*.38,y-h/2+3,w*.76,5,'#8a7652');
  }
  if(o.style==='chapel'){
    poly([[x-w*.28,y-h/2+5],[x,y-h/2-29],[x+w*.28,y-h/2+5]],'#35392d');
    px(x-4,y-h/2-21,8,19,'#b1aa89');px(x-2,y-h/2-18,4,13,'#343a2c');
    px(x-4,y-h/2-13,8,3,'#b7aa81');
  }
  if(o.style==='farmhouse'){
    poly([[x-w*.52,y-h/2+7],[x,y-h/2-23],[x+w*.52,y-h/2+7]],'#4f342b');
    px(x-18,y-h/2+3,36,7,'#6c4937');px(x+16,y-h/2-17,9,24,'#342e25');
    if(Math.sin(state.elapsed*2.1+o.x)>.75)px(x+w*.18,y-h/2+17,15,13,'#c99c55');
  }
}
function drawEvidence(o){
  const x=o.x-camera.x+shakeX;
  const y=o.y-camera.y+shakeY;
  if(x<-20||y<-20||x>W+20||y>H+20)return;
  if(o.found){
    px(x-5,y-4,10,8,'#313b2e');
    return;
  }
  const pulse=.5+.5*Math.sin(state.elapsed*4+o.x);
  ctx.fillStyle='rgba(212,185,108,'+(.08+pulse*.12)+')';
  ctx.beginPath();
  ctx.arc(x,y,16+pulse*9,0,Math.PI*2);
  ctx.fill();
  px(x-8,y-8,16,16,'#5a4c2d');
  px(x-5,y-5,10,10,pulse>.5?'#e2ca86':'#a48c56');
  px(x-2,y-2,4,4,'#f6edc2');
  px(x-12,y-1,3,2,'#c9aa68');
}
function drawLoot(o){
  if(o.found)return;
  const x=o.x-camera.x;
  const y=o.y-camera.y;
  if(x<-20||y<-20||x>W+20||y>H+20)return;
  const pulse=Math.sin(state.elapsed*3+o.y)>0;
  px(x-8,y-6,16,12,'#354134');
  px(x-6,y-7,12,2,'#7e815a');
  px(x-5,y-4,10,7,'#b09b67');
  px(x-3,y-2,6,3,pulse?'#e8d49b':'#7e764f');
}
function drawExit(o){
  const x=o.x-camera.x;
  const y=o.y-camera.y;
  const rescued=survivors.filter(s=>s.found||s.following||s.delivered).length;
  const unlocked=rescued>=2;
  const pulse=.5+.5*Math.sin(state.elapsed*4.5);
  ctx.save();
  if(unlocked){
    ctx.globalCompositeOperation='lighter';
    const glow=ctx.createRadialGradient(x,y,4,x,y,72+12*pulse);
    glow.addColorStop(0,'rgba(236,207,119,.38)');
    glow.addColorStop(1,'rgba(236,207,119,0)');
    ctx.fillStyle=glow;ctx.fillRect(x-90,y-90,180,180);
  }
  ctx.restore();
  px(x-32,y-18,64,36,'#858776');
  px(x-25,y-11,50,16,'#28362d');
  px(x-24,y+9,12,5,'#a72d30');
  px(x+12,y+9,12,5,'#a72d30');
  px(x-19,y-8,13,8,'#6e8172');
  px(x+6,y-8,13,8,'#6e8172');
  px(x-7,y-24,14,7,unlocked?'#e3c875':'#cfc7a5');
  ctx.fillStyle=unlocked?'#ffe8a1':'#d5d0ad';
  ctx.font='bold 11px monospace';
  ctx.textAlign='center';
  ctx.fillText(unlocked?'ESCAPE · ENTER BEACON':'EXTRACTION',x,y-34);
  if(unlocked){
    ctx.strokeStyle='rgba(255,225,140,'+(.4+.45*pulse)+')';
    ctx.lineWidth=2;
    ctx.beginPath();ctx.ellipse(x,y+2,46+8*pulse,32+6*pulse,0,0,Math.PI*2);ctx.stroke();
  }else{
    ctx.fillStyle='#e7dfba';ctx.font='9px monospace';ctx.fillText('RESCUE 2 PEOPLE',x,y+32);
  }
}
function drawSurvivors(){
  for(const s of survivors){
    if(s.delivered)continue;
    const x=s.x-camera.x;
    const y=s.y-camera.y;
    if(x<-30||y<-30||x>W+30||y>H+30)continue;
    px(x-7,y-7,14,15,'#242a25');
    px(x-5,y-12,10,8,'#8a7560');
    px(x-5,y-2,10,8,s.following?'#65785a':'#726c56');
    px(x-5,y+6,4,6,'#272b25');
    px(x+1,y+6,4,6,'#272b25');
    if(!s.found){
      ctx.strokeStyle='rgba(173,206,148,.45)';
      ctx.strokeRect(x-12,y-17,24,32);
    }
    if(s.following){
      ctx.fillStyle='#a8c88e';
      ctx.font='9px monospace';
      ctx.textAlign='center';
      ctx.fillText('FOLLOWING',x,y-20);
    }
  }
}
function drawCrawler(c){
  if(c.dead)return;
  const x=c.x-camera.x+shakeX;
  const y=c.y-camera.y+shakeY;
  if(x<-45||y<-45||x>W+45||y>H+45)return;
  const step=Math.sin(c.phase*8)*3;
  px(x-9,y-5,18,11,'#10120f');
  px(x-7,y-8+step,14,7,'#26271e');
  px(x-4,y-10+step,8,5,'#37382a');
  px(x-11,y-2,5,4,'#10120f');
  px(x+6,y-2,5,4,'#10120f');
  px(x-7,y+3,4,5,'#0d100d');
  px(x+4,y+3,4,5,'#0d100d');
  px(x-3,y-7+step,2,2,'#d54d40');
  px(x+2,y-7+step,2,2,'#d54d40');
  if(c.stunned>0){ctx.strokeStyle='rgba(202,187,151,.8)';ctx.lineWidth=2;ctx.beginPath();ctx.arc(x,y,17+Math.sin(state.elapsed*12)*2,0,Math.PI*2);ctx.stroke();}
  if(c.alert){
    ctx.fillStyle='rgba(188,56,51,.25)';
    ctx.beginPath();
    ctx.arc(x,y,19,0,Math.PI*2);
    ctx.fill();
  }
}
function drawSmilerContactLost(){
  if(!monster||!monster.active||!monster.hidden||state.floor!=='outside')return;
  const pulse=.5+.5*Math.sin(state.elapsed*5.8);
  ctx.save();
  ctx.fillStyle='rgba(2,3,3,.92)';
  ctx.fillRect(W*.5-143,Math.max(82,H*.13),286,45);
  ctx.strokeStyle='rgba(164,38,39,'+(.58+.35*pulse)+')';
  ctx.lineWidth=1.5;
  ctx.strokeRect(W*.5-143,Math.max(82,H*.13),286,45);
  ctx.textAlign='center';
  ctx.font='bold 12px monospace';
  ctx.fillStyle='#e6d5c8';
  ctx.fillText('VISUAL CONTACT LOST',W*.5,Math.max(82,H*.13)+17);
  ctx.font='bold 8px monospace';
  ctx.fillStyle='#b46a65';
  ctx.fillText('NO FOOTSTEPS // NO SIGNAL // DO NOT TURN BACK',W*.5,Math.max(82,H*.13)+32);
  ctx.restore();
}
function drawMonster(){
  if(!monster.active||monster.hidden)return;
  const x=monster.x-camera.x+shakeX;
  const y=monster.y-camera.y+shakeY;
  if(x<-140||y<-150||x>W+140||y>H+150)return;
  const bob=monster.frozenByLight?0:Math.sin(monster.phase*3.7)*3;
  const twitch=monster.frozenByLight?0:Math.sin(monster.phase*15)*1.8;
  const lurch=monster.stun>0||monster.frozenByLight?0:Math.sin(monster.phase*8)*2;
  if(monster.reappearGlow>0){ctx.save();ctx.globalCompositeOperation='screen';const pulse=monster.reappearGlow/.9;const ring=ctx.createRadialGradient(x,y,3,x,y,56*pulse+8);ring.addColorStop(0,'rgba(146,20,29,'+(.16*pulse)+')');ring.addColorStop(.45,'rgba(98,8,17,'+(.10*pulse)+')');ring.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=ring;ctx.fillRect(x-62,y-70,124,140);ctx.restore();}
  ctx.save();
  ctx.globalAlpha=monster.stun>0?.72:1;
  ctx.fillStyle='rgba(0,0,0,.6)';
  ctx.beginPath();
  ctx.ellipse(x,y+28,29,8,0,0,Math.PI*2);
  ctx.fill();
  px(x-18,y-29+bob,36,53,'#020302');
  px(x-15,y-49+bob,30,27,'#050605');
  px(x-11,y-64+bob,22,20,'#030403');
  px(x-8,y-69+bob,16,8,'#070807');
  px(x-21,y-27+bob,7,43,'#030403');
  px(x+14,y-28+bob,7,44,'#030403');
  px(x-24-twitch,y-4+bob,6,28,'#020302');
  px(x+19+twitch,y-2+bob,6,30,'#020302');
  px(x-27-twitch,y+17+bob,5,9,'#030403');
  px(x+22+twitch,y+18+bob,5,9,'#030403');
  px(x-23-twitch,y+25+bob,3,5,'#050605');
  px(x-19-twitch,y+24+bob,3,4,'#050605');
  px(x+21+twitch,y+26+bob,3,5,'#050605');
  px(x+17+twitch,y+24+bob,3,4,'#050605');
  const nearReveal=dist(player.x,player.y,monster.x,monster.y)<220;
  if(state.huntActive||monster.reappearGlow>0||nearReveal){
    const eyePulse=.55+.45*Math.sin(monster.phase*17.5);
    ctx.save();ctx.globalCompositeOperation='screen';
    for(const ex of [x-6,x+6]){
      const glow=ctx.createRadialGradient(ex,y-39+bob,0,ex,y-39+bob,18+(state.huntActive?12:0));
      glow.addColorStop(0,'rgba(255,40,35,'+(.22+.28*eyePulse)+')');
      glow.addColorStop(.35,'rgba(187,13,23,'+(.12+.16*eyePulse)+')');
      glow.addColorStop(1,'rgba(105,4,9,0)');
      ctx.fillStyle=glow;ctx.fillRect(ex-32,y-72+bob,64,64);
    }
    ctx.restore();
  }
  px(x-15,y+17,10,28,'#050605');
  px(x+5,y+17,10,28,'#050605');
  px(x-12,y+40,10,5,'#090a08');
  px(x+4,y+40,10,5,'#090a08');
  px(x-13,y-46+bob,26,9,'#070807');
  px(x-11,y-42+bob,22,7,'#11120f');
  px(x-9,y-42+bob,6,5,monster.frozenByLight?'#fff4cf':'#f4d5a3');
  px(x+3,y-42+bob,6,5,monster.frozenByLight?'#fff4cf':'#f4d5a3');
  px(x-7,y-41+bob,3,4,monster.frozenByLight?'#ff4b43':'#b8322b');
  px(x+4,y-41+bob,3,4,monster.frozenByLight?'#ff4b43':'#b8322b');
  px(x-5,y-30+bob,10,3,'#591a1a');
  px(x-9,y-28+bob,18,4,'#b9aa95');
  for(let tooth=0;tooth<6;tooth++)px(x-8+tooth*3,y-27+bob,1,4,tooth%2?'#221b18':'#eee0c3');
  px(x-10,y-23+bob,20,2,'#2c1715');
  px(x-8,y-18+bob,4,3,'#201815');
  px(x+5,y-18+bob,4,3,'#201815');
  px(x-4,y-27+bob,2,3,'#161512');
  px(x+1,y-27+bob,2,3,'#161512');
  px(x-9,y-19+bob,18,2,'#28231e');
  px(x-6,y-14+bob,12,2,'#191a15');
  px(x-16,y-4+bob,4,11,'#28221b');
  px(x+12,y-3+bob,4,11,'#28221b');
  for(let i=0;i<4;i++){
    px(x-25+i*2+twitch,y+18+i%2*3,2,7,'#0a0b09');
    px(x+20+i*2-twitch,y+18+i%2*3,2,7,'#0a0b09');
  }
  ctx.globalAlpha=1;
  if(monster.stun>0){
    px(x-22,y-72,44,2,'#dfc789');
    px(x-11,y-69,22,2,'#9e8a56');
  }
  const d=dist(player.x,player.y,monster.x,monster.y);
  if(d<300){
    ctx.strokeStyle='rgba(174,38,35,'+(.08+.06*(.5+.5*Math.sin(monster.phase*9)))+')';
    ctx.lineWidth=2;
    ctx.beginPath();
    ctx.ellipse(x,y+2,23+lurch,39,0,0,Math.PI*2);
    ctx.stroke();
  }
  ctx.restore();
}
function drawPatrolSirenWorldGlow(){
  const x=245-camera.x+shakeX;
  const y=278-camera.y+shakeY;
  if(x<-140||y<-140||x>W+140||y>H+140)return;
  const redOn=Math.sin(state.elapsed*13)>0;
  const lights=[{x:x-3,y:y-18,color:redOn?'rgba(247,43,50,.46)':'rgba(36,80,228,.12)'},{x:x+3,y:y-18,color:redOn?'rgba(36,80,228,.12)':'rgba(247,43,50,.46)'}];
  ctx.save();ctx.globalCompositeOperation='screen';
  for(const light of lights){
    const g=ctx.createRadialGradient(light.x,light.y,0,light.x,light.y,75);
    g.addColorStop(0,light.color);g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g;ctx.fillRect(light.x-75,light.y-75,150,150);
  }
  ctx.restore();
}
function drawPlayer(){
  if(player.hidden)return;
  const x=player.x-camera.x+shakeX;
  const y=player.y-camera.y+shakeY;
  const spec=specs[state.selectedCharacter];
  const leg=player.moving?Math.sin(player.step)*4:0;
  const bob=player.moving?Math.abs(Math.sin(player.step*2))*1.65:Math.sin(state.elapsed*1.7)*.45;
  const lean=player.moving?Math.sin(player.step)*.035:0;
  ctx.save();
  ctx.translate(Math.round(x),Math.round(y-bob));
  ctx.rotate(lean);
  ctx.rotate(player.angle);
  if(player.invulnerable>0&&Math.floor(state.elapsed*24)%2===0)ctx.globalAlpha=.5;
  px(-9,-8,18,17,'#080d0a');
  px(-7,-7,14,14,spec.color);
  px(-11,-6+leg*.22,5,11,spec.color);
  px(6,-6-leg*.22,5,11,spec.color);
  px(-7,-13,14,6,'#20261d');
  px(-6,-15,12,5,spec.shirt);
  px(-5,-16,10,3,'#c1b180');
  px(-7,7+leg,5,7,'#2b2c24');
  px(2,7-leg,5,7,'#2b2c24');
  px(2,-3,17,4,'#0b0e0b');
  px(15,-4,5,3,'#c9c5ac');
  px(-3,-2,4,3,'#e4d0a0');
  if(state.selectedCharacter==='hugo'){
    px(-6,-17,12,3,'#28241c');
    px(-5,-14,10,2,'#b5a16e');
    px(-2,-3,3,3,'#d4c7a5');
  }
  if(state.selectedCharacter==='yumi'){
    px(-8,-17,16,5,'#201816');
    px(-9,-13,3,12,'#201816');
    px(6,-13,3,12,'#201816');
    px(-4,-14,8,3,'#b8a5a0');
    px(-2,-3,3,3,'#d4c7a5');
  }
  ctx.restore();
}
function drawFireflies(){
  for(const f of fireflies){
    const x=f.x-camera.x+Math.sin(f.phase)*12;
    const y=f.y-camera.y+Math.cos(f.phase*.7)*9;
    if(x<0||y<0||x>W||y>H)continue;
    const alpha=.2+.45*(.5+.5*Math.sin(f.phase*2));
    ctx.fillStyle='rgba(182,202,119,'+alpha+')';
    ctx.fillRect(x,y,2,2);
    if(alpha>.45){
      ctx.fillStyle='rgba(151,177,104,.09)';
      ctx.fillRect(x-4,y-4,10,10);
    }
  }
}
function drawBulletEffects(){
  for(const b of bullets){
    const x=b.x-camera.x;
    const y=b.y-camera.y;
    px(x-2,y-2,5,5,'#f7daa0');
    px(x-1,y-1,2,2,'#fff7d9');
  }
  for(const p of particles){
    const x=p.x-camera.x;
    const y=p.y-camera.y;
    ctx.globalAlpha=clamp(p.life/.4,0,1);
    px(x,y,p.size||2,p.size||2,p.color||'#e4c78b');
    ctx.globalAlpha=1;
  }
}
function drawRain(){
  ctx.strokeStyle='rgba(154,179,173,.27)';
  ctx.lineWidth=1;
  ctx.beginPath();
  for(const r of raindrops){
    ctx.moveTo(r.x,r.y);
    ctx.lineTo(r.x-4,r.y+r.length);
  }
  ctx.stroke();
  ctx.fillStyle='rgba(141,164,156,.035)';
  ctx.fillRect(0,0,W,H);
}
function flashlightAngle(){
  if(!player)return 0;
  if(state.controlMode==='mobile')return player.angle||0;
  const target=worldCoordinates(pointer.x,pointer.y);
  const dx=target.x-player.x;
  const dy=target.y-player.y;
  if(Math.hypot(dx,dy)<24)return player.angle||0;
  return angleTo(player.x,player.y,target.x,target.y);
}
function drawMaskCone(x,y,angle,reach,halfAngle,ambientAlpha,haloRadius){
  const l=lightCtx;
  l.save();
  l.setTransform(dpr,0,0,dpr,0,0);
  l.clearRect(0,0,W,H);
  l.globalCompositeOperation='source-over';
  l.fillStyle='rgba(0,0,0,'+ambientAlpha+')';
  l.fillRect(0,0,W,H);
  l.globalCompositeOperation='destination-out';
  const halo=l.createRadialGradient(x,y,0,x,y,haloRadius);
  halo.addColorStop(0,'rgba(0,0,0,.96)');
  halo.addColorStop(.50,'rgba(0,0,0,.83)');
  halo.addColorStop(1,'rgba(0,0,0,0)');
  l.fillStyle=halo;
  l.beginPath();
  l.arc(x,y,haloRadius,0,Math.PI*2);
  l.fill();
  if(flashlight&&flashlightBattery>0){
    for(const band of [{spread:1.34,alpha:.10},{spread:1.20,alpha:.13},{spread:1.08,alpha:.18}]){
      l.save();
      l.globalAlpha=band.alpha;
      l.beginPath();l.moveTo(x,y);l.arc(x,y,reach*.98,angle-halfAngle*band.spread,angle+halfAngle*band.spread);l.closePath();l.clip();
      const feather=l.createRadialGradient(x,y,7,x,y,reach*.98);
      feather.addColorStop(0,'rgba(0,0,0,1)');feather.addColorStop(.72,'rgba(0,0,0,.9)');feather.addColorStop(1,'rgba(0,0,0,0)');
      l.fillStyle=feather;l.fillRect(x-reach,y-reach,reach*2,reach*2);
      l.restore();
    }
    l.save();
    l.beginPath();
    l.moveTo(x,y);
    l.arc(x,y,reach,angle-halfAngle,angle+halfAngle);
    l.closePath();
    l.clip();
    const beam=l.createRadialGradient(x,y,5,x,y,reach);
    beam.addColorStop(0,'rgba(0,0,0,1)');
    beam.addColorStop(.61,'rgba(0,0,0,1)');
    beam.addColorStop(.79,'rgba(0,0,0,.995)');
    beam.addColorStop(.92,'rgba(0,0,0,.83)');
    beam.addColorStop(1,'rgba(0,0,0,0)');
    l.fillStyle=beam;
    l.fillRect(x-reach,y-reach,reach*2,reach*2);
    l.restore();
    l.save();
    l.globalCompositeOperation='source-over';
    l.beginPath();
    l.moveTo(x,y);
    l.arc(x,y,reach,angle-halfAngle,angle+halfAngle);
    l.closePath();
    l.clip();
    const glow=l.createRadialGradient(x,y,9,x,y,reach);
    glow.addColorStop(0,'rgba(226,240,204,.17)');
    glow.addColorStop(.17,'rgba(206,228,190,.105)');
    glow.addColorStop(.55,'rgba(177,202,158,.055)');
    glow.addColorStop(.86,'rgba(159,186,146,.018)');
    glow.addColorStop(1,'rgba(159,186,146,0)');
    l.fillStyle=glow;
    l.fillRect(x-reach,y-reach,reach*2,reach*2);
    l.restore();
  }
  l.restore();
  ctx.save();
  ctx.globalCompositeOperation='source-over';
  ctx.drawImage(lightCanvas,0,0,W,H);
  ctx.restore();
}
function flashlightFlickerPulse(){
  const timer=state.flashlightFlickerTimer||0;
  const t=state.elapsed;
  if(timer>0){
    const p=t%1.11;
    return p<.052||(p>.18&&p<.226)||(p>.62&&p<.664)||(p>.91&&p<.951);
  }
  const natural=flashlight&&flashlightBattery>0&&state.intensity>.72;
  const p=t%8.4;
  return natural&&(p<.055||(p>1.14&&p<1.19));
}
function drawLighting(){
  const x=player.x-camera.x+shakeX;
  const y=player.y-camera.y+shakeY;
  const working=flashlight&&flashlightBattery>0;
  const angle=flashlightAngle();
  const flicker=flashlightFlickerPulse();
  drawMaskCone(x,y,angle,working?(flicker?215:590):1,flicker?.31:.34,state.lightning>0?0.22:1.0,working?(flicker?25:38):1);
  if(state.lightning>0){
    ctx.fillStyle='rgba(191,211,204,'+Math.min(.84,state.lightning*1.15)+')';
    ctx.fillRect(0,0,W,H);
    ctx.fillStyle='rgba(0,0,0,.22)';
    ctx.fillRect(0,0,W,H);
  }
  const vignette=ctx.createRadialGradient(W/2,H/2,Math.min(W,H)*.18,W/2,H/2,Math.max(W,H)*.78);
  vignette.addColorStop(0,'rgba(0,0,0,0)');
  vignette.addColorStop(.63,'rgba(0,0,0,.055)');
  vignette.addColorStop(1,'rgba(0,0,0,.44)');
  ctx.fillStyle=vignette;
  ctx.fillRect(0,0,W,H);
  if(monster&&monster.active&&!monster.hidden){
    const d=dist(player.x,player.y,monster.x,monster.y);
    if(d<285){
      const panic=(state.huntActive?.055:.025)+(state.huntActive?.075:.045)*(.5+.5*Math.sin(state.elapsed*(state.huntActive?13:10)));
      ctx.fillStyle='rgba(112,4,7,'+panic+')';
      ctx.fillRect(0,0,W,H);
      if(d<145&&Math.sin(state.elapsed*18)>.92){
        ctx.fillStyle='rgba(210,220,196,.035)';
        ctx.fillRect(0,0,W,H);
      }
    }
  }
}

function drawThreatMarkers(){
  if(!player||state.helpTimer<=0)return;
  const marks=[];
  if(state.floor==='outside'){
    for(const c of crawlers)if(!c.dead)marks.push({x:c.x,y:c.y,label:c.stunned>0?'CRAWLER / STAGGERED':'CRAWLER',color:c.stunned>0?'#c6d3a2':'#d96a66'});
    if(monster&&monster.active){
      const hidden=!!monster.hidden;
      marks.push({x:hidden?monster.pendingX:monster.x,y:hidden?monster.pendingY:monster.y,label:hidden?'SIGNAL LOST':'THE SMILER',color:'#f1b5ae'});
    }
  }else if(state.indoorPresence&&state.indoorPresence.timer>0){
    marks.push({x:state.indoorPresence.x,y:state.indoorPresence.y,label:'INDOOR PRESENCE',color:'#efb2b2'});
  }
  if(!marks.length)return;
  ctx.save();
  const pxs=player.x-camera.x+shakeX,pys=player.y-camera.y+shakeY;
  for(const mark of marks){
    const tx=mark.x-camera.x+shakeX,ty=mark.y-camera.y+shakeY;
    const dx=tx-pxs,dy=ty-pys;
    const onScreen=tx>24&&tx<W-24&&ty>24&&ty<H-24;
    let x=tx,y=ty;
    if(!onScreen){
      const scale=Math.min((W*.5-28)/Math.max(1,Math.abs(dx)),(H*.5-28)/Math.max(1,Math.abs(dy)));
      x=clamp(pxs+dx*scale,22,W-22);y=clamp(pys+dy*scale,22,H-22);
    }
    const pulse=.5+.5*Math.sin(state.elapsed*11+(mark.x+mark.y)*.003);
    ctx.globalAlpha=.66+.32*pulse;
    ctx.strokeStyle=mark.color;ctx.fillStyle=mark.color;ctx.lineWidth=2;
    ctx.beginPath();ctx.arc(x,y,onScreen?9+3*pulse:7+2*pulse,0,Math.PI*2);ctx.stroke();
    if(!onScreen){
      const a=Math.atan2(dy,dx);
      ctx.save();ctx.translate(x,y);ctx.rotate(a);ctx.beginPath();ctx.moveTo(10,0);ctx.lineTo(-5,-5);ctx.lineTo(-3,0);ctx.lineTo(-5,5);ctx.closePath();ctx.fill();ctx.restore();
    }
    ctx.globalAlpha=.95;ctx.font='bold 8px monospace';ctx.textAlign='center';ctx.textBaseline='bottom';
    const label=onScreen?mark.label:mark.label+' / DIRECTION';
    ctx.fillStyle='#030504';ctx.fillRect(x-62,y-22,124,12);
    ctx.fillStyle=mark.color;ctx.fillText(label,x,y-12);
  }
  ctx.globalAlpha=.88;ctx.textAlign='center';ctx.textBaseline='top';ctx.font='bold 9px monospace';
  ctx.fillStyle='#030504';ctx.fillRect(W*.5-112,7,224,19);
  ctx.fillStyle='#d8d9c8';ctx.fillText('PARTNER SIGNAL PULSE · THREAT POSITIONS',W*.5,11);
  ctx.restore();
}

function drawWorld(){
  if(state.prologueStage!=='swamp'){drawPrologue();return;}
  screenJitter();
  if(state.floor==='inside'){
    drawInterior();
    drawSurvivors();
    drawIndoorPresence();
    drawIndoorEcho();
    drawPlayer();
    drawBulletEffects();
    drawIndoorDust();
    drawLightingInterior();
    drawScreamPulse();
    drawThreatMarkers();
    drawIndoorWayfinding();
    drawMini();
    drawRealityText();
    if(state.sceneFade>0){ctx.fillStyle='rgba(0,0,0,'+state.sceneFade+')';ctx.fillRect(0,0,W,H);}
    return;
  }
  drawGround();
  drawPuddles();
  drawFootpaths();
  drawRoad();
  drawReeds();
  for(const t of trees)drawTree(t);
  for(const o of objects){
    if(o.missing)continue;
    if(o.type==='building')drawBuilding(o);
    if(o.type==='evidence')drawEvidence(o);
    if(o.type==='loot')drawLoot(o);
    if(o.type==='exit')drawExit(o);
  }
  drawSurvivors();
  for(const c of crawlers)drawCrawler(c);
  drawMonster();
  drawFalseSignal();
  drawPlayer();
  drawOutdoorMemoryEcho();
  drawBulletEffects();
  drawFireflies();
  drawRain();
  drawLighting();
  drawScreamPulse();
  drawThreatMarkers();
  drawFalseFigure();
  drawSurvivorGuidance();
  drawTrailPhantom();
  drawMini();
  drawRealityText();
  drawSmilerContactLost();
  if(state.sceneFade>0){ctx.fillStyle='rgba(0,0,0,'+state.sceneFade+')';ctx.fillRect(0,0,W,H);}
}
function drawInteriorBase(room,sx,sy){
  if(!interiorBaseCache.canvas||interiorBaseCache.room!==room){
    const cache=document.createElement('canvas');
    cache.width=room.w;
    cache.height=room.h;
    const g=cache.getContext('2d',{alpha:false});
    g.fillStyle=room.color||'#292e25';g.fillRect(0,0,room.w,room.h);
    for(let y=0;y<room.h;y+=32){
      for(let x=0;x<room.w;x+=32){
        const n=seeded(x,y);
        g.fillStyle=n>.5?'#414437':'#393e32';g.fillRect(x,y,32,32);
        g.fillStyle=n>.5?'#34382d':'#2c332a';g.fillRect(x+2,y+2,28,28);
        if(n>.82){g.fillStyle='#4b4c3b';g.fillRect(x+5,y+12,18,2);g.fillStyle='#1d241c';g.fillRect(x+8,y+15,7,1);}
        if(n<.12){g.fillStyle='#252d25';g.fillRect(x+4,y+4,2,17);g.fillStyle='#4b4836';g.fillRect(x+6,y+14,10,2);}
        if(n>.25&&n<.29){g.fillStyle='#1b241d';g.fillRect(x+2,y+25,28,1);g.fillStyle='#151e17';g.fillRect(x+14,y+27,1,4);}
        if(n>.59&&n<.63){g.fillStyle='#6a6148';g.fillRect(x+6,y+6,2,2);g.fillStyle='#1c241d';g.fillRect(x+10,y+10,1,6);}
      }
    }
    for(let i=0;i<18;i++){
      const wx=28+seeded(i,3)*Math.max(1,room.w-56);
      const wy=42+seeded(i,8)*Math.max(1,room.h-84);
      const n=seeded(i,13);
      if(n>.35&&n<.52){g.fillStyle='#24251e';g.fillRect(wx,wy,8+seeded(i,2)*22,2);g.fillRect(wx+3,wy+2,2,7);}
      if(n>.84){g.fillStyle='#50302b';g.fillRect(wx,wy,3,2);g.fillStyle='#352522';g.fillRect(wx+2,wy+2,2,4);}
    }
    g.fillStyle='#171d15';g.fillRect(0,0,room.w,24);g.fillRect(0,0,24,room.h);g.fillRect(room.w-24,0,24,room.h);g.fillRect(0,room.h-24,room.w,24);
    interiorBaseCache={room,canvas:cache};
  }
  ctx.drawImage(interiorBaseCache.canvas,sx,sy);
}
function drawInterior(){
  if(!state.room)return;
  const room=state.room;
  px(0,0,W,H,'#131811');
  const sx=-camera.x+shakeX;
  const sy=-camera.y+shakeY;
  drawInteriorBase(room,sx,sy);
  for(const p of room.props)drawFurniture(p,sx,sy);
  for(const item of room.items){
    if(item.found||item.missing)continue;
    const x=item.x+sx;
    const y=item.y+sy;
    const pulse=Math.sin(state.elapsed*4)>0;
    if(item.type==='sideTask'){
      const phase=.5+.5*Math.sin(state.elapsed*3.1);
      ctx.save();ctx.globalCompositeOperation='screen';
      const glow=ctx.createRadialGradient(x,y,2,x,y,32+phase*11);
      glow.addColorStop(0,'rgba(119,7,18,.35)');glow.addColorStop(.5,'rgba(72,3,10,.13)');glow.addColorStop(1,'rgba(0,0,0,0)');
      ctx.fillStyle=glow;ctx.fillRect(x-46,y-46,92,92);ctx.restore();
      ctx.strokeStyle=phase>.5?'#b74d48':'#5c2529';ctx.lineWidth=2;ctx.beginPath();ctx.arc(x,y,9+phase*3,0,Math.PI*2);ctx.stroke();
      px(x-4,y-4,8,8,'#050505');px(x-2,y-9,4,18,'#b33439');px(x-8,y-2,16,4,'#b33439');
      ctx.fillStyle='#dfb6a9';ctx.font='bold 7px monospace';ctx.textAlign='center';ctx.fillText('ANCHOR',x,y+22);
    }else if(item.type==='intakeDesk'){
      px(x-22,y-12,44,20,'#151b15');
      px(x-18,y-9,36,12,'#3d503a');
      px(x-13,y-7,26,8,'#92ad77');
      px(x-5,y-5,10,4,'#172316');
      px(x-25,y-15,50,2,pulse?'#d2c077':'#59684b');
      ctx.fillStyle='#c7d2b6';ctx.font='bold 7px monospace';ctx.textAlign='center';ctx.fillText('INTAKE',x,y+19);
    }else if(item.type==='note'){
      px(x-8,y-6,16,12,'#a59a70');
      px(x-5,y-3,10,2,'#514c38');
      px(x-5,y,8,2,'#6c6143');
      if(pulse)px(x-10,y-8,20,2,'#d1b96f');
    }else if(item.type==='memorial'){
      const halo=.42+.22*Math.sin(state.elapsed*1.15);
      ctx.save();ctx.globalCompositeOperation='screen';
      const memorialGlow=ctx.createRadialGradient(x,y,2,x,y,42);
      memorialGlow.addColorStop(0,'rgba(213,190,126,'+halo+')');memorialGlow.addColorStop(1,'rgba(0,0,0,0)');
      ctx.fillStyle=memorialGlow;ctx.fillRect(x-44,y-44,88,88);ctx.restore();
      px(x-23,y-27,46,48,'#2a281f');px(x-20,y-24,40,42,'#a18b5e');px(x-17,y-21,34,36,'#111811');
      px(x-14,y-18,12,11,'#7f8b78');px(x-12,y-16,8,2,'#c4b88e');px(x-8,y-14,2,6,'#c4b88e');px(x-15,y-12,14,2,'#c4b88e');
      px(x+3,y-18,12,11,'#464a3c');px(x+5,y-15,8,4,'#b3a477');px(x+4,y-10,3,3,'#080a08');px(x+12,y-10,3,3,'#080a08');
      px(x-14,y-3,28,2,'#655b3e');px(x-13,y+1,26,2,'#8f8057');px(x-9,y+5,18,2,'#cabb91');
      ctx.fillStyle='#e6d4a8';ctx.font='bold 7px monospace';ctx.textAlign='center';ctx.fillText('REMEMBER',x,y+31);
    }else if(item.type==='witness'){
      px(x-8,y-14,16,14,'#080b08');
      px(x-6,y-22,12,10,'#8b8064');
      px(x-8,y-24,16,4,'#171a13');
      px(x-5,y-5,4,3,'#d0b88a');
      px(x+2,y-5,4,3,'#d0b88a');
      if(pulse){px(x-12,y-27,24,2,'#bca66e');}
    }else{
      px(x-8,y-5,16,10,'#7f7959');
      px(x-4,y-2,8,4,'#c9b57a');
    }
  }
  const ex=room.exit.x+sx;
  const ey=room.exit.y+sy;
  const exitPulse=.55+.45*Math.sin(state.elapsed*4.5);
  ctx.save();ctx.globalCompositeOperation='lighter';
  const exitGlow=ctx.createRadialGradient(ex,ey-17,2,ex,ey-17,46);
  exitGlow.addColorStop(0,'rgba(229,196,103,'+(.24*exitPulse)+')');exitGlow.addColorStop(1,'rgba(229,196,103,0)');
  ctx.fillStyle=exitGlow;ctx.fillRect(ex-48,ey-64,96,94);ctx.restore();
  px(ex-39,ey-27,78,25,'#101710');
  px(ex-31,ey-22,62,17,'#4b6044');
  px(ex-24,ey-19,48,11,'#7f9a68');
  ctx.fillStyle='#f1d995';ctx.font='bold 11px monospace';ctx.textAlign='center';ctx.shadowColor='#efd37d';ctx.shadowBlur=8;ctx.fillText('EXIT',ex,ey-31);ctx.shadowBlur=0;
  for(let i=0;i<10;i++){
    const x=(i*89+35+state.elapsed*5)%room.w+sx;
    const y=(i*41+70)%room.h+sy;
    px(x,y,1,1,'#9e966b');
  }
  const textY=27;
  px(32,sy+32,room.w-64,1,'#6a6248');
  ctx.fillStyle='#d4c69d';
  ctx.textAlign='center';
  ctx.font='11px monospace';
  ctx.fillText(room.title,W/2,30);
  drawRainAtWindows(sx,sy,room);
}
function updateIndoorEcho(dt){
  if(!state.running||state.paused||state.gameOver||state.prologueStage!=='swamp')return;
  if(state.floor!=='inside'||!state.room||!player){
    indoorEcho.active=false;
    indoorEchoHistory=[];
    indoorEchoSampleTimer=0;
    indoorEchoRoomId='';
    return;
  }
  const roomId=state.room.id;
  if(indoorEchoRoomId!==roomId){
    indoorEchoRoomId=roomId;
    indoorEchoHistory=[];
    indoorEcho.roomAge=0;
    indoorEcho.cooldown=8+Math.random()*6;
    indoorEcho.active=false;
    indoorEchoSampleTimer=0;
  }
  indoorEcho.roomAge+=dt;
  indoorEcho.phase+=dt;
  indoorEcho.cooldown=Math.max(0,indoorEcho.cooldown-dt);
  indoorEchoSampleTimer-=dt;
  if(indoorEchoSampleTimer<=0){
    indoorEchoHistory.push({x:player.x,y:player.y,angle:player.angle||0,at:state.elapsed,roomId});
    indoorEchoSampleTimer=.28;
    while(indoorEchoHistory.length&&state.elapsed-indoorEchoHistory[0].at>13)indoorEchoHistory.shift();
  }
  if(indoorEcho.active){
    indoorEcho.timer-=dt;
    if(indoorEcho.timer<=0){
      indoorEcho.active=false;
      indoorEcho.cooldown=18+Math.random()*14;
    }
    return;
  }
  const eventKey='afterimage-'+roomId;
  if(indoorEcho.roomAge<9||indoorEcho.cooldown>0||state.horrorEventFlags[eventKey]||indoorEchoHistory.length<5)return;
  const candidates=indoorEchoHistory.filter(p=>p.roomId===roomId&&state.elapsed-p.at>2.6&&state.elapsed-p.at<7.3&&dist(player.x,player.y,p.x,p.y)>145&&dist(player.x,player.y,p.x,p.y)<440);
  let point=candidates.length?choose(candidates):null;
  if(!point){
    const side=player.x<state.room.w/2?1:-1;
    point={x:clamp(player.x+side*225,48,state.room.w-48),y:clamp(player.y+(player.y<state.room.h/2?125:-125),48,state.room.h-48),angle:player.angle||0};
  }
  indoorEcho={active:true,timer:2.45,cooldown:19+Math.random()*12,x:point.x,y:point.y,angle:point.angle||0,phase:Math.random()*20,roomId,roomAge:indoorEcho.roomAge};
  state.horrorEventFlags[eventKey]=true;
  state.intensity=Math.max(state.intensity,.8);
  state.screenShake=Math.max(state.screenShake,.1);
  sound('door');
  voiceNoise(choose(['left','right']),.14);
  if(state.options.voiceWhispers){
    const line=choose(['You left yourself in this room.','That is where you were standing a moment ago.','Do not walk toward the person wearing your uniform.','It learned your walk before it learned your name.']);
    triggerWhisper(line,choose(['left','right']),'BODYCAM PLAYBACK');
  }
  if(Math.random()<.35)toast('BODYCAM FRAME DELAY: YOUR LAST POSITION IS STILL MOVING.',2.6);
}
function drawIndoorEcho(){
  if(!indoorEcho.active||indoorEcho.timer<=0||state.floor!=='inside'||!state.room||indoorEcho.roomId!==state.room.id||!player)return;
  const sx=indoorEcho.x-camera.x+shakeX;
  const sy=indoorEcho.y-camera.y+shakeY;
  if(sx<-70||sy<-90||sx>W+70||sy>H+90)return;
  const d=dist(player.x,player.y,indoorEcho.x,indoorEcho.y);
  const beamAngle=angleTo(player.x,player.y,indoorEcho.x,indoorEcho.y);
  const delta=Math.abs(Math.atan2(Math.sin(beamAngle-flashlightAngle()),Math.cos(beamAngle-flashlightAngle())));
  const beamOn=flashlight&&flashlightBattery>0&&d<545&&delta<.36;
  if(!beamOn)return;
  const focused=delta<.16;
  const fade=Math.min(1,indoorEcho.timer*1.3);
  ctx.save();
  ctx.translate(Math.round(sx),Math.round(sy));
  ctx.rotate(indoorEcho.angle||0);
  ctx.globalAlpha=fade*(focused?.42:.93);
  ctx.fillStyle='#010201';
  ctx.fillRect(-11,-10,22,22);
  ctx.fillRect(-8,-19,16,10);
  ctx.fillRect(-7,-30,14,13);
  ctx.fillRect(-13,-8,5,20);
  ctx.fillRect(8,-8,5,20);
  ctx.fillRect(-8,11,6,15);
  ctx.fillRect(3,11,6,15);
  ctx.fillStyle='#121711';
  ctx.fillRect(-8,-7,16,15);
  ctx.fillStyle='#353b2e';
  ctx.fillRect(-8,-7,3,2);
  ctx.fillRect(5,-7,3,2);
  ctx.fillStyle='#050605';
  ctx.fillRect(-4,-29,3,3);
  ctx.fillRect(2,-29,3,3);
  if(!focused&&Math.sin(indoorEcho.phase*12)>.05){
    ctx.fillStyle='#d9d2b8';
    ctx.shadowColor='#d1d7ba';ctx.shadowBlur=8;
    ctx.fillRect(-4,-27,2,2);ctx.fillRect(3,-27,2,2);
    ctx.shadowBlur=0;
  }
  ctx.fillStyle='rgba(1,2,1,.92)';
  ctx.fillRect(-50,31,100,12);
  ctx.fillStyle=focused?'#777d6c':'#d2cbb0';
  ctx.font='bold 7px monospace';ctx.textAlign='center';
  ctx.fillText(focused?'FRAME LOST':'YOU / SIX SECONDS AGO',0,39);
  ctx.restore();
}
function updateOutdoorMemoryEcho(dt){
  if(!state.running||state.paused||state.gameOver||state.prologueStage!=='swamp'||!player)return;
  if(state.floor!=='outside'){
    outdoorMemoryEcho.active=false;
    outdoorEchoSampleTimer=0;
    return;
  }
  outdoorEchoSampleTimer-=dt;
  if(outdoorEchoSampleTimer<=0){
    outdoorEchoSampleTimer=.24;
    const last=outdoorEchoTrail[outdoorEchoTrail.length-1];
    if(player.moving&&(!last||dist(last.x,last.y,player.x,player.y)>15)){
      outdoorEchoTrail.push({x:player.x,y:player.y,angle:player.angle||0,at:state.elapsed});
    }
    while(outdoorEchoTrail.length&&state.elapsed-outdoorEchoTrail[0].at>17)outdoorEchoTrail.shift();
    if(outdoorEchoTrail.length>90)outdoorEchoTrail.splice(0,outdoorEchoTrail.length-90);
  }
  outdoorMemoryEcho.phase+=dt*2.7;
  outdoorMemoryEcho.cooldown=Math.max(0,outdoorMemoryEcho.cooldown-dt);
  if(outdoorMemoryEcho.active){
    outdoorMemoryEcho.timer-=dt;
    const d=dist(player.x,player.y,outdoorMemoryEcho.x,outdoorMemoryEcho.y);
    const a=angleTo(player.x,player.y,outdoorMemoryEcho.x,outdoorMemoryEcho.y);
    const delta=Math.abs(Math.atan2(Math.sin(a-flashlightAngle()),Math.cos(a-flashlightAngle())));
    const lit=flashlight&&flashlightBattery>0&&d<510&&delta<.3;
    if(lit){outdoorMemoryEcho.focused+=dt;if(outdoorMemoryEcho.focused>.34)outdoorMemoryEcho.timer-=dt*2.3;}
    if(outdoorMemoryEcho.timer<=0){
      outdoorMemoryEcho.active=false;
      outdoorMemoryEcho.cooldown=24+Math.random()*21;
      sound('radio');
      for(let i=0;i<7;i++)addParticle({x:outdoorMemoryEcho.x+(Math.random()-.5)*22,y:outdoorMemoryEcho.y+(Math.random()-.5)*38,vx:(Math.random()-.5)*38,vy:-8-Math.random()*24,life:.22+Math.random()*.3,color:choose(['#11150f','#6a2428','#b5b8a0']),size:2+Math.random()*2});
      if(outdoorMemoryEcho.seen){
        toast('THE FIGURE DISINTEGRATES INTO THE LAST FRAME OF YOUR OWN BODYCAM.',2.7);
        if(!state.horrorEventFlags.outdoorEchoRecord){
          state.horrorEventFlags.outdoorEchoRecord=true;
          caseRecords.push({id:'outdoor-memory-echo',name:'Duplicated bodycam frame',detail:'A second copy of the officer appeared on the bodycam trail, replaying a movement recorded several seconds earlier.',analysis:'The figure did not approach. It performed a movement the officer had already made. When illuminated continuously, it vanished between frames.',kind:'anomaly',studied:false});
        }
      }
    }
    return;
  }
  if(!monster||!monster.active||state.huntActive||state.radioIncidentActive||state.personalScareTimer>0||state.elapsed<38||outdoorMemoryEcho.cooldown>0)return;
  const eligible=collectedClueCount()>=1||state.exploredRoomIds.length>=1||state.huntsSurvived>=1;
  if(!eligible||outdoorEchoTrail.length<8||Math.random()>dt*.22)return;
  const candidates=outdoorEchoTrail.filter(p=>state.elapsed-p.at>4.1&&state.elapsed-p.at<13.8&&dist(player.x,player.y,p.x,p.y)>145&&dist(player.x,player.y,p.x,p.y)<510&&!blockedAt(p.x,p.y,player.r+2));
  let point=candidates.length?choose(candidates):null;
  if(!point){
    const behind=(player.angle||0)+Math.PI+(Math.random()-.5)*.8;
    const radius=205+Math.random()*95;
    const x=clamp(player.x+Math.cos(behind)*radius,62,WORLD.w-62);
    const y=clamp(player.y+Math.sin(behind)*radius,62,WORLD.h-62);
    if(!blockedAt(x,y,player.r+2))point={x,y,angle:player.angle||0};
  }
  if(!point)return;
  outdoorMemoryEcho={active:true,timer:1.15+Math.random()*.85,cooldown:24+Math.random()*22,x:point.x,y:point.y,angle:point.angle||0,phase:Math.random()*12,focused:0,seen:false};
  state.intensity=Math.max(state.intensity,.74);
  state.screenShake=Math.max(state.screenShake,.08);
  sound('step');
  voiceNoise(choose(['left','right']),.10);
  if(state.options.voiceWhispers&&state.voiceCooldown<=0)triggerWhisper(choose(['That was your walk. You are still walking.','The bodycam remembers you in a place you never stood.','Do not approach your own shadow.','It is copying the way you leave.']),choose(['left','right']),'DELAYED BODYCAM FRAME');
}
function drawOutdoorMemoryEcho(){
  if(!outdoorMemoryEcho.active||outdoorMemoryEcho.timer<=0||state.floor!=='outside'||state.prologueStage!=='swamp')return;
  const sx=outdoorMemoryEcho.x-camera.x+shakeX;
  const sy=outdoorMemoryEcho.y-camera.y+shakeY;
  if(sx<-65||sy<-95||sx>W+65||sy>H+95)return;
  const d=dist(player.x,player.y,outdoorMemoryEcho.x,outdoorMemoryEcho.y);
  const a=angleTo(player.x,player.y,outdoorMemoryEcho.x,outdoorMemoryEcho.y);
  const delta=Math.abs(Math.atan2(Math.sin(a-flashlightAngle()),Math.cos(a-flashlightAngle())));
  const lit=flashlight&&flashlightBattery>0&&d<510&&delta<.3;
  const focused=lit&&delta<.15;
  const fade=Math.min(1,outdoorMemoryEcho.timer*2.1);
  if(lit)outdoorMemoryEcho.seen=true;
  ctx.save();
  ctx.translate(Math.round(sx),Math.round(sy));
  ctx.rotate(outdoorMemoryEcho.angle||0);
  ctx.globalAlpha=fade*(lit?.94:.42);
  ctx.fillStyle='#010201';
  ctx.fillRect(-10,-9,20,20);
  ctx.fillRect(-8,-21,16,12);
  ctx.fillRect(-7,-31,14,12);
  ctx.fillRect(-13,-8,5,21);
  ctx.fillRect(8,-8,5,21);
  ctx.fillRect(-8,10,6,16);
  ctx.fillRect(3,10,6,16);
  ctx.fillStyle='#0e130e';ctx.fillRect(-8,-7,16,13);
  if(lit&&!focused){ctx.fillStyle='#d5d1bd';ctx.fillRect(-4,-29,3,2);ctx.fillRect(2,-29,3,2);}
  if(focused){
    ctx.fillStyle='#6f1118';ctx.shadowColor='#df2631';ctx.shadowBlur=9;
    ctx.fillRect(-5,-29,3,2);ctx.fillRect(2,-29,3,2);ctx.shadowBlur=0;
    if(Math.sin(state.elapsed*48)>0){ctx.globalAlpha*=.65;ctx.fillStyle='#d7ded1';ctx.fillRect(-10,-34,20,27);}
  }
  ctx.globalAlpha=fade*(lit?.9:.25);
  ctx.fillStyle='rgba(0,0,0,.94)';ctx.fillRect(-61,31,122,12);
  ctx.font='bold 7px monospace';ctx.textAlign='center';ctx.fillStyle=focused?'#ecb7ad':'#c7cbb8';ctx.fillText(focused?'FRAME OUT OF ORDER':'YOU / OLD BODYCAM FRAME',0,39);
  ctx.restore();
}
function beginSilencePocket(){
  state.soundVoidTotal=(state.soundVoidTotal||0)+1;
  state.soundVoidTimer=2.3+Math.random()*1.1;
  state.soundVoidCooldown=47+Math.random()*27;
  state.intensity=Math.max(state.intensity,.9);
  state.screenShake=Math.max(state.screenShake,.10);
  sound('radio');
  setAmbientBed(false);
  toast('THE RAIN STOPS. THE INSECTS STOP. YOUR FOOTSTEPS ARE THE ONLY SOUND LEFT.',3.7);
  if(state.options.voiceWhispers)triggerWhisper('You can hear me now. This is what your body sounds like from the inside.','center','CHANNEL ZERO');
}
function updateNightmareAtmosphere(dt){
  if(!state.running||state.paused||state.gameOver||state.prologueStage!=='swamp')return;
  state.soundVoidCooldown=Math.max(0,(state.soundVoidCooldown||0)-dt);
  if(state.soundVoidTimer>0){
    state.soundVoidTimer=Math.max(0,state.soundVoidTimer-dt);
    if(state.soundVoidTimer===0){
      setAmbientBed(true);
      if(state.options.voiceWhispers)triggerWhisper('The rain is back. It was never rain.','right','FIELD MICROPHONE');
      state.intensity=Math.max(state.intensity,.68);
    }
    return;
  }
  if(state.soundVoidTotal>=3||state.soundVoidCooldown>0||state.elapsed<44||!monster||!monster.active||state.huntActive||state.radioIncidentActive||state.personalScareTimer>0)return;
  if(state.floor==='inside'&&state.room&&state.elapsed>80&&Math.random()<dt*.025){beginSilencePocket();return;}
  if(state.floor==='outside'&&state.elapsed>55&&Math.random()<dt*.018){beginSilencePocket();return;}
}

function updateHauntingDirector(dt){
  if(!state.running||state.paused||state.gameOver||state.prologueStage!=='swamp')return;
  const flags=state.horrorEventFlags;
  if(state.elapsed>48&&collectedClueCount()>=2&&!flags.unknownPartnerTransmission&&!state.radioIncidentActive){
    flags.unknownPartnerTransmission=true;
    state.intensity=Math.max(state.intensity,.83);
    state.noise=Math.max(state.noise,.25);
    sound('radio');
    setTimeout(()=>{
      if(!state.running||state.gameOver||state.prologueStage!=='swamp')return;
      addPartnerMessage('I am standing inside the next building. Leave the flashlight off. I need you to come alone.','unknown');
      tone(49,.72,'sawtooth',.08,-22);
      toast('AN UNVERIFIED MESSAGE HAS ENTERED THE SECURE CHAT.',3.5);
      setTimeout(()=>{
        if(!state.running||state.gameOver||state.prologueStage!=='swamp')return;
        addPartnerMessage('That message was not me. My radio has been unplugged for the last minute. Please confirm my call sign before acting.','incoming');
        if(state.options.voiceWhispers)triggerWhisper('You listened to the wrong voice. It thanked you for coming.','left','SECURE CHAT / DUPLICATE SENDER');
      },2200);
    },450);
  }
  if(state.stationComplete&&!flags.stationPartnerMimic){
    flags.stationPartnerMimic=true;
    state.intensity=Math.max(state.intensity,.92);
    state.flashlightFlickerTimer=Math.max(state.flashlightFlickerTimer||0,.45);
    sound('radio');
    tone(61,.72,'triangle',.07,-27);
    toast('SECURE CHANNEL: AN UNREAD MESSAGE ARRIVED WHILE YOUR RADIO WAS DISCONNECTED.',3.6);
    setTimeout(()=>{
      if(state.running&&!state.gameOver&&state.prologueStage==='swamp')addPartnerMessage('I can see you standing at the station intake desk. Please tell me you are not still inside.','incoming');
    },850);
    setTimeout(()=>{
      if(state.running&&!state.gameOver&&state.prologueStage==='swamp')addPartnerMessage('I did not send that last message. I am looking at your live feed. You are outside. Keep walking.','incoming');
    },2450);
    if(state.options.voiceWhispers)triggerWhisper('You checked six visitors. The seventh was already holding the camera.','center','CAMERA 04');
  }
  if(state.exploredRoomIds.length>=3&&!flags.threeRoomMemory){
    flags.threeRoomMemory=true;
    state.intensity=Math.max(state.intensity,.76);
    state.apparitionCooldown=Math.min(state.apparitionCooldown,2.2);
    sound('door');
    toast('THREE BUILDINGS SEARCHED. YOUR BODYCAM FOOTAGE SHOWS YOU ENTERING EACH ONE TWICE.',4.0);
    if(state.options.voiceWhispers)triggerWhisper('You are not discovering these rooms. You are remembering them.','right','BODYCAM TRANSCRIPT');
    caseRecords.push({id:'echoed-building-route',name:'Impossible bodycam route',detail:'The bodycam appears to record two entries into each of three different buildings, though only one visit is logged.',analysis:'This is not a timestamp issue. The second version of the officer arrives before the first version leaves.',kind:'anomaly',studied:true});
  }
  if(collectedClueCount()>=4&&!flags.fourClueCountervoice){
    flags.fourClueCountervoice=true;
    state.intensity=Math.max(state.intensity,.8);
    state.noise=Math.max(state.noise,.35);
    sound('radio');
    setTimeout(()=>{
      if(state.running&&!state.gameOver&&state.prologueStage==='swamp')addPartnerMessage('Your fourth evidence record just updated. There is a new line underneath it: “PARTNER COUNT: 0”. Do you see that?','incoming');
    },620);
    if(state.options.voiceWhispers)triggerWhisper('Evidence does not prove what happened. It proves what is still happening.','left','UNKNOWN CASE REVIEWER');
  }
  if(state.keysFound&&!flags.relayVoiceAnswered){
    flags.relayVoiceAnswered=true;
    sound('radio');
    state.screenShake=Math.max(state.screenShake,.13);
    toast('THE RELAY KEY IS WARM. THE KEYRING HAS TWO SHADOWS.',3.3);
    if(state.options.voiceWhispers)triggerWhisper('Put the key down. I can open the door from my side.','behind','RELAY CHANNEL / NO SENDER');
  }
}
function drawIndoorPresence(){
  if(state.floor!=='inside'||!state.room||!monster||!monster.active)return;
  const a=state.indoorPresence;
  if(!a||a.timer<=0)return;
  const sx=a.x-camera.x+shakeX;
  const sy=a.y-camera.y+shakeY;
  if(sx<-80||sy<-100||sx>W+80||sy>H+100)return;
  const d=dist(player.x,player.y,a.x,a.y);
  const targetAngle=angleTo(player.x,player.y,a.x,a.y);
  const da=Math.abs(Math.atan2(Math.sin(targetAngle-flashlightAngle()),Math.cos(targetAngle-flashlightAngle())));
  const beamOn=flashlight&&flashlightBattery>0&&d<470&&da<.38;
  const alpha=beamOn?1:.96;
  ctx.save();ctx.globalAlpha=alpha;
  const lean=Math.sin(a.phase*5)*3;
  ctx.fillStyle='#020403';
  ctx.beginPath();ctx.moveTo(sx-12,sy-72);ctx.lineTo(sx+11,sy-70);ctx.lineTo(sx+19,sy-48);ctx.lineTo(sx+14,sy-20);ctx.lineTo(sx+27,sy+25);ctx.lineTo(sx+9,sy+19);ctx.lineTo(sx+3,sy-5);ctx.lineTo(sx-6,sy+29);ctx.lineTo(sx-25,sy+35);ctx.lineTo(sx-16,sy-9);ctx.lineTo(sx-21,sy-45);ctx.closePath();ctx.fill();
  ctx.fillRect(sx-22+lean,sy-45,7,31);ctx.fillRect(sx+14-lean,sy-43,7,34);
  if(!beamOn||Math.sin(a.phase*21)>.55){ctx.fillStyle='#f0d5b8';ctx.shadowColor='#c20e22';ctx.shadowBlur=14;ctx.fillRect(sx-7,sy-58,4,2);ctx.fillRect(sx+4,sy-58,4,2);ctx.shadowBlur=0;}
  ctx.fillStyle='rgba(0,0,0,.9)';ctx.fillRect(sx-28,sy+38,56,8);
  ctx.restore();
}
function drawIndoorDust(){
  if(state.floor!=='inside'||!state.room)return;
  const reach=flashlight&&flashlightBattery>0?460:26;
  for(let i=0;i<34;i++){
    const a=seeded(i,17)*Math.PI*2;
    const r=(seeded(i,19)*reach+((state.elapsed*9+i*7)%reach));
    const wx=player.x+Math.cos(a)*r;
    const wy=player.y+Math.sin(a)*r*.72;
    const sx=wx-camera.x+Math.sin(state.elapsed*1.4+i)*3;
    const sy=wy-camera.y+Math.cos(state.elapsed*1.1+i)*2;
    if(sx<0||sy<0||sx>W||sy>H)continue;
    const alpha=flashlight&&flashlightBattery>0?.16+.18*(.5+.5*Math.sin(state.elapsed*2+i)):.035;
    ctx.fillStyle='rgba(202,202,166,'+alpha+')';ctx.fillRect(sx,sy,i%6===0?2:1,i%6===0?2:1);
  }
}
function drawIndoorWayfinding(){
  if(state.floor!=='inside'||!state.room)return;
  const titleY=Math.max(55,H*.085);
  ctx.save();ctx.fillStyle='rgba(3,8,5,.82)';ctx.fillRect(W/2-154,titleY-17,308,24);ctx.strokeStyle='rgba(133,157,117,.48)';ctx.strokeRect(W/2-154,titleY-17,308,24);ctx.fillStyle='#d4c69f';ctx.font='bold 10px monospace';ctx.textAlign='center';ctx.fillText(state.room.title+'  //  SEARCH THE ROOM',W/2,titleY-2);ctx.restore();
  const dx=state.room.exit.x-player.x;
  const dy=state.room.exit.y-player.y;
  const a=Math.atan2(dy,dx);
  const d=Math.round(Math.hypot(dx,dy));
  const x=W*.5;const y=H*.73;
  ctx.save();ctx.fillStyle='rgba(3,8,5,.78)';ctx.fillRect(x-73,y-14,146,28);
  ctx.strokeStyle='rgba(211,181,107,.62)';ctx.lineWidth=1;ctx.strokeRect(x-73,y-14,146,28);
  ctx.translate(x-49,y);ctx.rotate(a+Math.PI/2);ctx.fillStyle='#f1d995';ctx.beginPath();ctx.moveTo(0,-7);ctx.lineTo(6,5);ctx.lineTo(0,2);ctx.lineTo(-6,5);ctx.closePath();ctx.fill();ctx.restore();
  ctx.fillStyle='#f1dfaa';ctx.font='bold 10px monospace';ctx.textAlign='left';ctx.fillText('EXIT ROUTE  '+d+'m',x-35,y+3);
}
function drawFurniture(p,sx,sy){
  const x=p.x+sx;
  const y=p.y+sy;
  if(p.t==='desk'){
    px(x-p.w/2,y-p.h/2+5,p.w,p.h,'#241f18');
    px(x-p.w/2+3,y-p.h/2,p.w-6,p.h-8,'#6c5337');
    px(x-p.w/2+8,y-p.h/2+5,p.w-16,p.h-18,'#886745');
    px(x-p.w/2+10,y+p.h/2-3,9,14,'#3c3021');
    px(x+p.w/2-19,y+p.h/2-3,9,14,'#3c3021');
    px(x-12,y-5,22,13,'#aaa58a');
    px(x-10,y-3,18,2,'#4c4b3b');
  }
  if(p.t==='cabinet'){
    px(x-p.w/2,y-p.h/2,p.w,p.h,'#25281e');
    px(x-p.w/2+4,y-p.h/2+4,p.w-8,p.h-8,'#63543a');
    px(x-2,y-p.h/2+6,3,p.h-12,'#2a2e22');
    px(x-p.w/2+9,y,3,5,'#c6b279');
    px(x+5,y,3,5,'#c6b279');
  }
  if(p.t==='shelves'){
    px(x-p.w/2,y-p.h/2,p.w,p.h,'#33291e');
    for(let yy=y-p.h/2+10;yy<y+p.h/2-5;yy+=25){
      px(x-p.w/2+3,yy,p.w-6,4,'#90704b');
      for(let xx=x-p.w/2+7;xx<x+p.w/2-9;xx+=19){
        px(xx,yy-9,9,9,choose(['#3d4e38','#595540','#4f3430','#5c5c45']));
      }
    }
  }
  if(p.t==='bed'){
    px(x-p.w/2,y-p.h/2,p.w,p.h,'#27251e');
    px(x-p.w/2+5,y-p.h/2+5,p.w-10,p.h-10,'#766c52');
    px(x-p.w/2+9,y-p.h/2+8,p.w-18,p.h-16,'#494d3a');
    px(x-p.w/2+9,y-p.h/2+8,p.w-18,14,'#a39a7e');
  }
  if(p.t==='table'){
    px(x-p.w/2,y-p.h/2,p.w,p.h,'#25251c');
    px(x-p.w/2+3,y-p.h/2+3,p.w-6,p.h-7,'#7b6140');
    px(x-p.w/2+7,y+p.h/2-1,7,15,'#332a1e');
    px(x+p.w/2-14,y+p.h/2-1,7,15,'#332a1e');
  }
  if(p.t==='console'){
    px(x-p.w/2,y-p.h/2,p.w,p.h,'#1b241e');
    px(x-p.w/2+6,y-p.h/2+6,p.w-12,p.h-12,'#35443a');
    for(let i=0;i<8;i++)px(x-p.w/2+12+i*21,y-p.h/2+17,7,6,choose(['#b4423c','#a8b079','#647d9c']));
    px(x-p.w/2+10,y+12,p.w-20,4,'#0d110e');
  }
}
function drawRainAtWindows(sx,sy,room){
  const windows=[{x:room.w*.22,y:28,w:34,h:8},{x:room.w*.76,y:28,w:34,h:8}];
  for(const w of windows){
    px(w.x+sx,w.y+sy,w.w,w.h,'#141d19');
    px(w.x+sx+3,w.y+sy+2,w.w-6,w.h-4,'#4d6b61');
    if(Math.sin(state.elapsed*2)>0)px(w.x+sx+5,w.y+sy+2,2,w.h-4,'#a3b9a6');
  }
}
function drawLightingInterior(){
  const x=player.x-camera.x+shakeX;
  const y=player.y-camera.y+shakeY;
  const working=flashlight&&flashlightBattery>0;
  const angle=flashlightAngle();
  const flicker=flashlightFlickerPulse();
  drawMaskCone(x,y,angle,working?(flicker?260:585):1,flicker?.46:.53,1.0,working?(flicker?28:44):1);
  if(flicker){
    ctx.fillStyle='rgba(0,0,0,.12)';
    ctx.fillRect(0,0,W,H);
  }
  if(monster&&monster.active&&!monster.hidden){
    const d=dist(player.x,player.y,monster.x,monster.y);
    if(d<260){
      ctx.fillStyle='rgba(100,0,5,'+(state.huntActive?.065+.055*(.5+.5*Math.sin(state.elapsed*14)):.025+.035*(.5+.5*Math.sin(state.elapsed*11)))+')';
      ctx.fillRect(0,0,W,H);
    }
  }
  const vignette=ctx.createRadialGradient(W/2,H/2,Math.min(W,H)*.18,W/2,H/2,Math.max(W,H)*.8);
  vignette.addColorStop(0,'rgba(0,0,0,0)');
  vignette.addColorStop(.62,'rgba(0,0,0,.08)');
  vignette.addColorStop(1,'rgba(0,0,0,.43)');
  ctx.fillStyle=vignette;
  ctx.fillRect(0,0,W,H);
}
function currentOutdoorTarget(){
  if(collectedClueCount()<6){
    const clues=objects.filter(o=>o.type==='evidence'&&!o.found&&!o.missing).sort((a,b)=>dist(player.x,player.y,a.x,a.y)-dist(player.x,player.y,b.x,b.y));
    if(clues.length)return {...clues[0],navKind:'clue',navLabel:'EVIDENCE · '+clues[0].name.toUpperCase()};
    const buildings=objects.filter(o=>o.type==='building'&&!state.exploredRoomIds.includes(o.room)).sort((a,b)=>dist(player.x,player.y,a.x,a.y)-dist(player.x,player.y,b.x,b.y));
    if(buildings.length)return {...buildings[0],navKind:'building',navLabel:'SEARCH FOR CLUES · '+buildings[0].name.toUpperCase()};
  }
  if(studyCount()<6)return {navKind:'casefile',navLabel:'OPEN CASE FILE [J] · STUDY '+(6-studyCount())+' MORE CLUE(S)'};
  if(validCrossReferenceCount()<4)return {navKind:'casefile',navLabel:'CASE FILE [J] · MAKE '+(4-validCrossReferenceCount())+' MORE DISTINCT COMPARISON(S)'};
  if(state.caseTheory!=='mimic-timeline')return {navKind:'casefile',navLabel:'CASE FILE [J] · SUBMIT A SUPPORTED THEORY'};
  if(!state.witnessInterviewed||state.witnessTrust<2){const b=objects.find(o=>o.id==='farmhouse');return b?{...b,navKind:'building',navLabel:state.witnessInterviewed?'RETURN TO SILAS VENN':'INTERVIEW SILAS VENN'}:null;}
  if(!state.stationComplete){const b=objects.find(o=>o.id==='station');return b?{...b,navKind:'building',navLabel:'SCREEN SIX STATION VISITORS'}:null;}
  if(!state.keysFound){const b=objects.find(o=>o.id==='tower');return b?{...b,navKind:'building',navLabel:'FIND THE RELAY OVERRIDE KEY'}:null;}
  if(state.exploredRoomIds.length<5){const bs=objects.filter(o=>o.type==='building'&&!state.exploredRoomIds.includes(o.room)).sort((a,b)=>dist(player.x,player.y,a.x,a.y)-dist(player.x,player.y,b.x,b.y));if(bs.length)return {...bs[0],navKind:'building',navLabel:'SEARCH BUILDING · '+bs[0].name.toUpperCase()};}
  const missing=survivors.filter(s=>!s.found&&!s.following&&!s.delivered).sort((a,b)=>dist(player.x,player.y,a.x,a.y)-dist(player.x,player.y,b.x,b.y));
  if(missing.length)return {...missing[0],navKind:'survivor',navLabel:'SOS · '+missing[0].name.toUpperCase()};
  const rescued=survivors.filter(s=>s.found||s.following||s.delivered).length;
  const exit=objects.find(o=>o.type==='exit');
  if(rescued>=2&&exit)return {...exit,navKind:'exit',navLabel:'EXTRACTION BEACON'};
  return null;
}
function drawSurvivorGuidance(){
  if(state.prologueStage!=='swamp'||state.floor!=='outside'||!state.running)return;
  const target=currentOutdoorTarget();
  if(!target)return;
  if(target.navKind==='casefile'){
    ctx.save();
    ctx.fillStyle='rgba(4,7,5,.94)';ctx.fillRect(W*.5-170,54,340,28);
    ctx.strokeStyle='rgba(221,193,115,.88)';ctx.lineWidth=1.4;ctx.strokeRect(W*.5-170,54,340,28);
    ctx.fillStyle='#f0d998';ctx.font='bold 10px monospace';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(target.navLabel,W*.5,68);
    ctx.restore();
    return;
  }
  const d=dist(player.x,player.y,target.x,target.y);
  const sx=target.x-camera.x+shakeX;
  const sy=target.y-camera.y+shakeY;
  const onScreen=sx>22&&sy>22&&sx<W-22&&sy<H-22;
  const isExit=target.navKind==='exit';
  const isSurvivor=target.navKind==='survivor';
  const hue=isExit?'rgba(255,221,139,':isSurvivor?'rgba(179,255,143,':target.navKind==='clue'?'rgba(255,207,106,':'rgba(151,207,222,';
  const solid=isExit?'#ffe7a3':isSurvivor?'#d8ffc0':target.navKind==='clue'?'#ffe0a0':'#c0edfa';
  const label=target.navLabel||target.name.toUpperCase();
  if(onScreen){
    const pulse=.5+.5*Math.sin(state.elapsed*(isExit?5:4.2));
    const bx=sx,by=sy-25;
    ctx.save();ctx.globalCompositeOperation='lighter';
    const glow=ctx.createRadialGradient(bx,by,2,bx,by,30+15*pulse);
    glow.addColorStop(0,hue+'.55)');glow.addColorStop(.35,hue+'.20)');glow.addColorStop(1,hue+'0)');
    ctx.fillStyle=glow;ctx.fillRect(bx-48,by-48,96,96);ctx.restore();
    ctx.strokeStyle=hue+(.65+.3*pulse)+')';ctx.lineWidth=2;ctx.beginPath();ctx.arc(bx,by,8+4*pulse,0,Math.PI*2);ctx.stroke();
    ctx.fillStyle=solid;ctx.beginPath();ctx.moveTo(bx,by-5);ctx.lineTo(bx+5,by);ctx.lineTo(bx,by+5);ctx.lineTo(bx-5,by);ctx.closePath();ctx.fill();
    ctx.strokeStyle=hue+'.8)';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(bx,by+10);ctx.lineTo(sx,sy-13);ctx.stroke();
    const labelW=Math.min(W-24,Math.max(132,Math.min(300,label.length*6.1)));
    ctx.fillStyle='rgba(3,10,5,.94)';ctx.fillRect(sx-labelW/2,sy-51,labelW,15);
    ctx.strokeStyle=isExit?'#d3b45e':isSurvivor?'#87ba72':target.navKind==='clue'?'#d8a84e':'#75aeba';ctx.strokeRect(sx-labelW/2,sy-51,labelW,15);
    ctx.fillStyle=solid;ctx.font='bold 8px monospace';ctx.textAlign='center';ctx.fillText(label.length>42?label.slice(0,40)+'…':label,sx,sy-40);
    const caption=isExit?'STEP INTO BEACON TO ESCAPE':isSurvivor?(d<150?'E / SEARCH TO RESCUE':Math.round(d)+'m TO SURVIVOR'):target.navKind==='clue'?(d<115?'E / SEARCH FOR EVIDENCE':Math.round(d)+'m · FOLLOW THE TRAIL'):d<145?'E / SEARCH BUILDING':Math.round(d)+'m · FOLLOW THE TRAIL';
    ctx.fillStyle=solid;ctx.font='bold 10px monospace';ctx.fillText(caption,sx,sy-62);
  }else{
    const pxp=clamp(player.x-camera.x,0,W),pyp=clamp(player.y-camera.y,0,H);
    const vx=sx-pxp,vy=sy-pyp,angle=Math.atan2(vy,vx);
    const marginX=Math.min(52,W*.13),marginTop=155,marginBottom=H-150;
    const scaleX=vx>0?(W-marginX-pxp)/vx:vx<0?(marginX-pxp)/vx:Infinity;
    const scaleY=vy>0?(marginBottom-pyp)/vy:vy<0?(marginTop-pyp)/vy:Infinity;
    let scale=Math.min(scaleX>0?scaleX:Infinity,scaleY>0?scaleY:Infinity);if(!Number.isFinite(scale))scale=1;
    const ax=clamp(pxp+vx*scale,marginX,W-marginX),ay=clamp(pyp+vy*scale,marginTop,marginBottom);
    ctx.save();ctx.translate(ax,ay);ctx.rotate(angle+Math.PI/2);ctx.fillStyle=solid;ctx.strokeStyle='#122211';ctx.lineWidth=3;
    ctx.beginPath();ctx.moveTo(0,-14);ctx.lineTo(10,10);ctx.lineTo(0,5);ctx.lineTo(-10,10);ctx.closePath();ctx.stroke();ctx.fill();ctx.restore();
    const short=label.length>24?label.slice(0,22)+'…':label;
    ctx.font='bold 8px monospace';const boxW=Math.min(W-20,Math.max(110,short.length*5.4+14));
    ctx.fillStyle='rgba(3,10,5,.94)';ctx.fillRect(ax-boxW/2,ay+14,boxW,16);
    ctx.strokeStyle=isExit?'#d3b45e':isSurvivor?'#87ba72':target.navKind==='clue'?'#d8a84e':'#75aeba';ctx.strokeRect(ax-boxW/2,ay+14,boxW,16);
    ctx.fillStyle=solid;ctx.textAlign='center';ctx.fillText(short+' · '+Math.round(d)+'m',ax,ay+25);
  }
}

function drawMini(){
  if(state.elapsed-lastMiniDraw<.12&&lastMiniFloor===state.floor&&lastMiniRoom===state.room)return;
  lastMiniDraw=state.elapsed;lastMiniFloor=state.floor;lastMiniRoom=state.room;
  const mw=mini.width;
  const mh=mini.height;
  mctx.fillStyle='#07100a';
  mctx.fillRect(0,0,mw,mh);
  if(state.floor==='inside'&&state.room){
    const room=state.room;
    const pad=8;
    const scale=Math.min((mw-pad*2)/room.w,(mh-pad*2)/room.h);
    const rw=room.w*scale,rh=room.h*scale;
    const ox=(mw-rw)/2,oy=(mh-rh)/2;
    mctx.fillStyle='#050806';mctx.fillRect(0,0,mw,mh);
    mctx.fillStyle='#22291f';mctx.fillRect(ox,oy,rw,rh);
    mctx.strokeStyle='#9b9470';mctx.lineWidth=1.5;mctx.strokeRect(ox,oy,rw,rh);
    mctx.fillStyle='#101710';
    for(const p of room.props){mctx.fillRect(ox+(p.x-p.w/2)*scale,oy+(p.y-p.h/2)*scale,Math.max(2,p.w*scale),Math.max(2,p.h*scale));mctx.strokeStyle='#4c5542';mctx.strokeRect(ox+(p.x-p.w/2)*scale,oy+(p.y-p.h/2)*scale,Math.max(2,p.w*scale),Math.max(2,p.h*scale));}
    const ex=ox+room.exit.x*scale,ey=oy+room.exit.y*scale;
    mctx.fillStyle='#f2d47e';mctx.beginPath();mctx.arc(ex,ey,3.3,0,Math.PI*2);mctx.fill();
    mctx.strokeStyle='rgba(242,212,126,.6)';mctx.beginPath();mctx.moveTo(ox+player.x*scale,oy+player.y*scale);mctx.lineTo(ex,ey);mctx.stroke();
    for(const item of room.items){if(item.found||item.missing)continue;const ix=ox+item.x*scale,iy=oy+item.y*scale;mctx.fillStyle=item.type==='witness'?'#9bd9ee':item.type==='note'?'#ffda75':'#99d997';mctx.fillRect(ix-2,iy-2,4,4);mctx.strokeStyle='rgba(255,232,160,.6)';mctx.strokeRect(ix-3,iy-3,6,6);}
    const pxp=ox+player.x*scale,pyp=oy+player.y*scale;
    mctx.fillStyle='#fff4c9';mctx.beginPath();mctx.arc(pxp,pyp,3.4,0,Math.PI*2);mctx.fill();
    mctx.strokeStyle='#fff4c9';mctx.lineWidth=1.5;mctx.beginPath();mctx.moveTo(pxp,pyp);mctx.lineTo(pxp+Math.cos(player.angle)*7,pyp+Math.sin(player.angle)*7);mctx.stroke();
    mctx.fillStyle='#d8cba2';mctx.font='bold 7px monospace';mctx.textAlign='center';mctx.fillText('ROOM MAP',mw/2,7);
    return;
  }
  mctx.fillStyle='#152319';
  mctx.fillRect(2,2,mw-4,mh-4);
  mctx.strokeStyle='#6b7354';
  mctx.lineWidth=1.15;
  for(const points of FOOTPATHS){
    mctx.beginPath();
    mctx.moveTo(points[0].x/WORLD.w*mw,points[0].y/WORLD.h*mh);
    for(let i=1;i<points.length;i++)mctx.lineTo(points[i].x/WORLD.w*mw,points[i].y/WORLD.h*mh);
    mctx.stroke();
  }
  mctx.strokeStyle='#5e604d';
  mctx.lineWidth=3;
  for(const points of roadNetworks()){
    mctx.beginPath();
    mctx.moveTo(points[0].x/WORLD.w*mw,points[0].y/WORLD.h*mh);
    for(let i=1;i<points.length;i++)mctx.lineTo(points[i].x/WORLD.w*mw,points[i].y/WORLD.h*mh);
    mctx.stroke();
  }
  for(const o of objects){
    if(o.type!=='building')continue;
    const bx=o.x/WORLD.w*mw,by=o.y/WORLD.h*mh;
    mctx.fillStyle=state.exploredRoomIds.includes(o.room)?'#66715e':'#a0a18a';mctx.fillRect(bx-2,by-2,4,4);
  }
  for(const o of objects){
    const x=o.x/WORLD.w*mw;
    const y=o.y/WORLD.h*mh;
    let color='#77826d';
    if(o.type==='evidence'&&!o.found)color='#e1be65';
    if(o.type==='loot'&&!o.found)color='#93c68c';
    if(o.type==='exit')color='#d5d0ad';
    mctx.fillStyle=color;
    mctx.fillRect(x-2,y-2,4,4);
  }
  for(const s of survivors){
    if(s.delivered)continue;
    const sx=s.x/WORLD.w*mw;
    const sy=s.y/WORLD.h*mh;
    const pulse=.5+.5*Math.sin(state.elapsed*4.2+(s.id==='wade'?1.4:0));
    mctx.beginPath();mctx.arc(sx,sy,5+2*pulse,0,Math.PI*2);
    mctx.strokeStyle=s.following?'rgba(183,225,143,.65)':'rgba(177,255,144,'+(0.55+.4*pulse)+')';mctx.lineWidth=1.4;mctx.stroke();
    mctx.fillStyle=s.following?'#e0f1b1':'#a9ff88';mctx.fillRect(sx-3,sy-3,7,7);
    mctx.strokeStyle='#071009';mctx.lineWidth=1;mctx.strokeRect(sx-3,sy-3,7,7);
    mctx.fillStyle='#071009';mctx.font='bold 6px monospace';mctx.textAlign='center';mctx.textBaseline='middle';mctx.fillText(s.id==='ana'?'M':'E',sx,sy+.2);
  }
  mctx.fillStyle='#b8dfa0';mctx.font='bold 7px monospace';mctx.textAlign='left';mctx.textBaseline='top';mctx.fillText('M/E = SURVIVOR',5,4);
  if(state.falseSignal.active){
    const fx=state.falseSignal.x/WORLD.w*mw,fy=state.falseSignal.y/WORLD.h*mh;
    const pulse=.5+.5*Math.sin(state.elapsed*9);
    mctx.fillStyle='rgba(94,239,165,'+(.4+.55*pulse)+')';mctx.fillRect(fx-3,fy-3,7,7);
    mctx.strokeStyle='rgba(94,239,165,.7)';mctx.strokeRect(fx-5,fy-5,11,11);
  }
  mctx.fillStyle='#fff0bc';
  mctx.fillRect(player.x/WORLD.w*mw-2,player.y/WORLD.h*mh-2,5,5);
  if(monster&&monster.active&&!monster.hidden){
    mctx.fillStyle='#e4413d';
    mctx.fillRect(monster.x/WORLD.w*mw-2,monster.y/WORLD.h*mh-2,5,5);
  }
  for(const c of crawlers){
    if(c.dead)continue;
    if(dist(player.x,player.y,c.x,c.y)<460){
      mctx.fillStyle='#bf4d47';
      mctx.fillRect(c.x/WORLD.w*mw-1,c.y/WORLD.h*mh-1,3,3);
    }
  }
}
function drawMenuArt(){
  const c=$('artCanvas');
  if(!c)return;
  const g=c.getContext('2d');
  const cw=c.width;
  const ch=c.height;
  g.clearRect(0,0,cw,ch);
  g.fillStyle='#070e0a';
  g.fillRect(0,0,cw,ch);
  for(let y=0;y<ch;y+=10){
    g.fillStyle=y<160?'#0b1810':y<260?'#112016':'#17221a';
    g.fillRect(0,y,cw,10);
  }
  for(let i=0;i<24;i++){
    const x=(i*67)%cw;
    const h=70+(i*31)%170;
    g.fillStyle=i%3===0?'#1b2d20':'#14251a';
    g.fillRect(x,180-h*.4,9,h);
    g.fillRect(x-16,210-h*.23,42,10);
    g.fillRect(x-10,170-h*.2,31,12);
  }
  g.fillStyle='#080d09';
  g.beginPath();
  g.moveTo(0,290);
  g.lineTo(93,230);
  g.lineTo(230,248);
  g.lineTo(320,292);
  g.lineTo(320,390);
  g.lineTo(0,390);
  g.fill();
  g.fillStyle='#34372d';
  g.beginPath();
  g.moveTo(72,390);
  g.lineTo(130,260);
  g.lineTo(191,260);
  g.lineTo(278,390);
  g.fill();
  g.strokeStyle='#817760';
  g.lineWidth=3;
  g.setLineDash([13,16]);
  g.beginPath();
  g.moveTo(175,390);
  g.lineTo(160,276);
  g.stroke();
  g.setLineDash([]);
  g.fillStyle='#050706';
  g.fillRect(197,180,27,87);
  g.fillRect(201,152,20,33);
  g.fillRect(194,200,6,34);
  g.fillRect(221,200,6,34);
  g.fillStyle='#b83d3c';
  g.fillRect(205,164,3,2);
  g.fillRect(215,164,3,2);
  g.fillStyle='#4f422e';
  g.fillRect(192,187,35,4);
  for(let i=0;i<38;i++){
    const x=(i*71)%cw;
    const y=(i*47)%ch;
    g.fillStyle=i%4===0?'#d6d0a6':'#7d9666';
    g.fillRect(x,y,1,1);
  }
  const fog=g.createLinearGradient(0,210,0,ch);
  fog.addColorStop(0,'rgba(9,16,10,0)');
  fog.addColorStop(1,'rgba(6,10,7,.94)');
  g.fillStyle=fog;
  g.fillRect(0,210,cw,ch-210);
}
function drawPortraits(){
  const ids=['charArt0','charArt1'];
  const keys=['hugo','yumi'];
  ids.forEach((id,index)=>{
    const c=$(id);
    const g=c.getContext('2d');
    const spec=specs[keys[index]];
    g.clearRect(0,0,64,64);
    g.fillStyle='#0a120c';
    g.fillRect(0,0,64,64);
    g.fillStyle='#1b2d20';
    g.fillRect(5,4,54,56);
    g.fillStyle=spec.color;
    g.fillRect(18,31,28,25);
    g.fillStyle=spec.shirt;
    g.fillRect(17,21,30,16);
    g.fillStyle='#d0c18e';
    g.fillRect(16,18,32,7);
    g.fillStyle='#171b15';
    g.fillRect(21,29,6,5);
    g.fillRect(37,29,6,5);
    g.fillStyle='#b8b9a5';
    g.fillRect(26,36,12,3);
    g.fillStyle='#171b15';
    g.fillRect(25,42,14,7);
    if(spec.gender==='male'){
      g.fillStyle=spec.hair;
      g.fillRect(21,10,22,7);
      g.fillRect(19,14,5,8);
      g.fillRect(40,14,5,8);
      g.fillStyle='#b5a16e';
      g.fillRect(21,18,22,3);
      g.fillStyle='#d2b975';
    }else{
      g.fillStyle=spec.hair;
      g.fillRect(20,9,24,9);
      g.fillRect(18,14,6,23);
      g.fillRect(40,14,6,23);
      g.fillRect(23,8,18,4);
      g.fillStyle='#c7b5a1';
      g.fillRect(22,18,20,3);
      g.fillStyle='#d2b975';
    }
    g.fillStyle='#d2b975';
    g.fillRect(12,36,5,10);
    g.fillRect(47,36,5,10);
    if(index===0){
      g.fillStyle='#d4bb76';
      g.fillRect(21,20,22,3);
      g.fillStyle='#6b7858';
      g.fillRect(17,25,30,4);
      g.fillStyle='#d6c18b';
      g.fillRect(29,32,6,5);
    }
    if(index===1){
      g.fillStyle='#626e58';
      g.fillRect(22,14,20,6);
      g.fillRect(20,19,24,4);
      g.fillStyle='#c9b6a0';
      g.fillRect(22,24,20,3);
      g.fillStyle='#d6c18b';
      g.fillRect(29,32,6,5);
    }
  });
}
let cloudAccount=null;
let cloudReturnScreen='menu';
let cloudRequestBusy=false;
function cloudEsc(value){return String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
function cloudMessage(message,kind=''){
  const box=$('cloudStatus');
  if(!box)return;
  box.className='account-status'+(kind?' '+kind:'');
  box.textContent=message;
}
async function cloudRequest(path,options={}){
  const config={method:options.method||'GET',credentials:'same-origin',headers:{'Content-Type':'application/json',...(options.headers||{})}};
  if(options.body!==undefined)config.body=JSON.stringify(options.body);
  const response=await fetch(path,config);
  let data={};
  try{data=await response.json();}catch(error){data={error:'The server returned an unreadable response.'};}
  if(!response.ok)throw new Error(data.error||('Request failed ('+response.status+').'));
  return data;
}
function cloudOpenAccount(source='menu'){
  cloudReturnScreen=source;
  if(source==='pause'||state.screen==='game')state.paused=true;
  setScreen('account');
  cloudMessage('Checking cloud database…');
  cloudRefreshAll();
}
function cloudCloseAccount(){
  if(cloudReturnScreen==='pause'){
    setScreen('pause');
    state.paused=true;
    return;
  }
  setScreen('menu');
}
function cloudSetIdentity(user){
  cloudAccount=user||null;
  const identity=$('accountIdentity');
  const login=$('accountLogin');
  const register=$('accountRegister');
  const logout=$('accountLogout');
  const staff=$('staffOverview');
  const staffBtn=$('refreshStaffOverview');
  if(cloudAccount){
    identity.innerHTML='<strong>'+cloudEsc(cloudAccount.username)+'</strong><br><span class="account-role">'+cloudEsc(String(cloudAccount.role||'player').toUpperCase())+'</span><br>Cloud profile connected.';
    login.classList.add('hidden');
    register.classList.add('hidden');
    logout.classList.remove('hidden');
    const isStaff=cloudAccount.role==='staff';
    staff.classList.toggle('hidden',!isStaff);
    staffBtn.classList.toggle('hidden',!isStaff);
  }else{
    identity.textContent='Not signed in.';
    login.classList.remove('hidden');
    register.classList.remove('hidden');
    logout.classList.add('hidden');
    staff.classList.add('hidden');
    staffBtn.classList.add('hidden');
  }
}
function cloudStats(){
  const survivorsCount=Array.isArray(survivors)?survivors.filter(x=>x.found||x.following||x.delivered).length:0;
  const deliveredCount=Array.isArray(survivors)?survivors.filter(x=>x.delivered).length:0;
  return {
    cluesCollected:collectedClueCount(),
    cluesStudied:studyCount(),
    crossReferences:validCrossReferenceCount(),
    caseTheory:state.caseTheory||'',
    witnessInterviewed:!!state.witnessInterviewed,
    witnessTrust:Number(state.witnessTrust)||0,
    stationComplete:!!state.stationComplete,
    stationCorrect:Number(state.stationCorrect)||0,
    stationProcessed:Number(state.stationProcessed)||0,
    survivors:survivorsCount,
    survivorsDelivered:deliveredCount,
    keysFound:!!state.keysFound,
    buildingsSearched:Array.isArray(state.exploredRoomIds)?state.exploredRoomIds.length:0,
    extractionHold:Number(state.extractionHold)||0,
    extractionSurvived:!!state.won,
    anchorsDestroyed:Array.isArray(state.anchorsDestroyed)?state.anchorsDestroyed.length:0,
    trueEnding:!!state.anchorsDisabled,
    huntsSurvived:Number(state.huntsSurvived)||0,
    elapsed:Number(state.elapsed)||0,
    kills:Number(state.kills)||0,
    shots:Number(state.shots)||0,
    won:!!state.won
  };
}
function cloudSnapshot(){
  if(!player)throw new Error('Start a patrol before saving progress.');
  const safeArray=(arr,max)=>Array.isArray(arr)?arr.slice(-max):[];
  return {
    schemaVersion:1,
    selectedCharacter:state.selectedCharacter==='yumi'?'yumi':'hugo',
    floor:state.floor==='inside'?'inside':'outside',
    roomId:state.floor==='inside'&&state.room?String(state.room.id||'checkpoint'):'',
    player:{x:Number(player.x)||0,y:Number(player.y)||0,angle:Number(player.angle)||0,hp:Number(player.hp)||0,stamina:Number(player.stamina)||0},
    inventory:{ammo:Number(ammo)||0,reserve:Number(reserve)||0,medkits:Number(medkits)||0,batteryCells:Number(batteryCells)||0,flashlightBattery:Number(flashlightBattery)||0,flashlight:!!flashlight},
    progress:{
      elapsed:Number(state.elapsed)||0,missionClock:Number(state.missionClock)||0,discovered:Number(state.discovered)||0,rescued:Number(state.rescued)||0,
      keysFound:!!state.keysFound,witnessInterviewed:!!state.witnessInterviewed,witnessTrust:Number(state.witnessTrust)||0,
      stationStage:String(state.stationStage||'idle'),stationQueuePosition:Number(state.stationQueuePosition)||0,stationQueue:safeArray(state.stationQueue,12),
      stationDecisions:state.stationDecisions||{},stationChecks:state.stationChecks||{},stationChats:state.stationChats||{},stationTopics:state.stationTopics||{},stationManifestEvents:state.stationManifestEvents||{},stationAuditTrail:safeArray(state.stationAuditTrail,30),stationRetryMode:!!state.stationRetryMode,stationThreat:Number(state.stationThreat)||0,stationIncidentLogged:!!state.stationIncidentLogged,stationFeedback:String(state.stationFeedback||''),stationComplete:!!state.stationComplete,stationCorrect:Number(state.stationCorrect)||0,stationProcessed:Number(state.stationProcessed)||0,
      exploredRoomIds:safeArray(state.exploredRoomIds,32),caseComparisons:safeArray(state.caseComparisons,32),caseTheory:String(state.caseTheory||''),theoryAttempts:Number(state.theoryAttempts)||0,
      missingIds:safeArray(state.missingIds,100),roomItemStates:state.roomItemStates||{},disappearanceLog:safeArray(state.disappearanceLog,100),exploredRooms:Number(state.exploredRooms)||0,
      kills:Number(state.kills)||0,shots:Number(state.shots)||0,anchorsDestroyed:safeArray(state.anchorsDestroyed,12),anchorsDisabled:!!state.anchorsDisabled,trueEnding:!!state.trueEnding,
      helpCount:Number(state.helpCount)||0,huntsSurvived:Number(state.huntsSurvived)||0,threatTier:Number(state.threatTier)||0,
      extractionStarted:!!state.extractionStarted,extractionHold:Number(state.extractionHold)||0,extractionWave1:!!state.extractionWave1,extractionWave2:!!state.extractionWave2,extractionWave3:!!state.extractionWave3,extractionWave4:!!state.extractionWave4,
      gameStats:cloudStats()
    },
    survivors:Array.isArray(survivors)?survivors.map(x=>({id:x.id,found:!!x.found,following:!!x.following,delivered:!!x.delivered,hp:Number(x.hp)||0,x:Number(x.x)||0,y:Number(x.y)||0})):[],
    objects:Array.isArray(objects)?objects.filter(x=>x.id).map(x=>({id:String(x.id),found:!!x.found,missing:!!x.missing})).slice(0,150):[],
    caseRecords:Array.isArray(caseRecords)?caseRecords.slice(-100).map(x=>({id:String(x.id||''),name:String(x.name||'Clue').slice(0,180),detail:String(x.detail||'').slice(0,500),analysis:String(x.analysis||'').slice(0,800),kind:String(x.kind||'evidence').slice(0,30),studied:!!x.studied})):[]
  };
}
async function cloudLoadAccount(){
  try{
    const result=await cloudRequest('/api/auth/me');
    cloudSetIdentity(result.user||null);
    cloudMessage(result.database?'MongoDB connected.':'Signed in.', 'good');
    if(cloudAccount)await cloudRefreshAll(true);
    return result;
  }catch(error){
    cloudSetIdentity(null);
    cloudMessage(error.message+' Configure MONGODB_URI and the Flask/staff environment variables on Render.', 'error');
    return null;
  }
}
async function cloudLogin(event){
  if(event)event.preventDefault();
  if(cloudRequestBusy)return;
  cloudRequestBusy=true;
  try{
    const result=await cloudRequest('/api/auth/login',{method:'POST',body:{username:$('accountUsername').value.trim(),password:$('accountPassword').value}});
    $('accountPassword').value='';
    cloudSetIdentity(result.user);
    cloudMessage('Signed in securely as '+result.user.username+'.','good');
    await cloudRefreshAll(true);
  }catch(error){cloudMessage(error.message,'error');}
  finally{cloudRequestBusy=false;}
}
async function cloudRegister(){
  if(cloudRequestBusy)return;
  cloudRequestBusy=true;
  try{
    const result=await cloudRequest('/api/auth/register',{method:'POST',body:{username:$('accountUsername').value.trim(),password:$('accountPassword').value}});
    $('accountPassword').value='';
    cloudSetIdentity(result.user);
    cloudMessage('Player account created. You are signed in.','good');
    await cloudRefreshAll(true);
  }catch(error){cloudMessage(error.message,'error');}
  finally{cloudRequestBusy=false;}
}
async function cloudLogout(){
  try{await cloudRequest('/api/auth/logout',{method:'POST',body:{}});}catch(error){}
  cloudSetIdentity(null);
  cloudMessage('Signed out. Local gameplay remains available.');
  await cloudRefreshLeaderboard();
  $('cloudSaveList').textContent='Sign in to view cloud saves.';
  $('cloudAchievementList').textContent='Sign in to sync achievements.';
}
async function cloudRefreshSaves(){
  if(!cloudAccount){$('cloudSaveList').textContent='Sign in to view cloud saves.';return;}
  try{
    const result=await cloudRequest('/api/saves');
    const list=$('cloudSaveList');list.replaceChildren();
    if(!result.saves.length){list.textContent='No cloud saves yet. Start a patrol, pause, open Account / Cloud Save, and save a slot.';return;}
    for(const save of result.saves){
      const row=document.createElement('div');row.className='account-row';
      const title=document.createElement('strong');title.textContent=String(save.slot||'slot').toUpperCase()+' · '+(save.character||'Unknown officer');
      const details=document.createElement('div');details.textContent='Updated '+(save.updatedAt||'recently')+' · '+(Number(save.cluesStudied)||0)+' clues studied · '+(Number(save.survivors)||0)+' people found';
      row.append(title,details);list.appendChild(row);
    }
  }catch(error){$('cloudSaveList').textContent=error.message;}
}
async function cloudSaveGame(){
  if(!cloudAccount){cloudMessage('Sign in before saving to MongoDB.','error');return;}
  const activePatrol=state.running||(state.screen==='account'&&cloudReturnScreen==='pause'&&!!player&&!state.gameOver);
  if(!activePatrol||!player||state.gameOver||state.prologueStage!=='swamp'){cloudMessage('Enter the woods and begin the investigation before saving progress.','error');return;}
  try{
    const slot=$('cloudSaveSlot').value;
    const payload=cloudSnapshot();
    const result=await cloudRequest('/api/saves',{method:'POST',body:{slot,payload}});
    cloudMessage('Saved '+slot+' to MongoDB at '+result.updatedAt+'.','good');
    await cloudRequest('/api/progress',{method:'POST',body:{stats:cloudStats()}});
    await cloudRefreshSaves();
    await cloudRefreshAchievements();
  }catch(error){cloudMessage(error.message,'error');}
}
function restoreCloudSnapshot(snapshot){
  if(!snapshot||typeof snapshot!=='object')throw new Error('This save is incomplete or damaged.');
  const selected=snapshot.selectedCharacter==='yumi'?'yumi':'hugo';
  state.selectedCharacter=selected;state.pendingCharacter=selected;
  resetGame();
  setPrologueStage('swamp');
  const prog=snapshot.progress&&typeof snapshot.progress==='object'?snapshot.progress:{};
  const inv=snapshot.inventory&&typeof snapshot.inventory==='object'?snapshot.inventory:{};
  state.elapsed=clamp(Number(prog.elapsed)||0,0,86400);
  state.missionClock=clamp(Number(prog.missionClock)||0,0,86400);
  state.discovered=clamp(Number(prog.discovered)||0,0,999);
  state.rescued=clamp(Number(prog.rescued)||0,0,2);
  state.keysFound=!!prog.keysFound;
  state.witnessInterviewed=!!prog.witnessInterviewed;
  state.witnessTrust=clamp(Number(prog.witnessTrust)||0,-10,10);
  state.stationStage=String(prog.stationStage||'idle');
  state.stationQueuePosition=clamp(Number(prog.stationQueuePosition)||0,0,6);
  state.stationQueue=Array.isArray(prog.stationQueue)?prog.stationQueue.slice(0,12):[];
  state.stationDecisions=prog.stationDecisions&&typeof prog.stationDecisions==='object'?prog.stationDecisions:{};
  state.stationChecks=prog.stationChecks&&typeof prog.stationChecks==='object'?prog.stationChecks:{};
  state.stationChats=prog.stationChats&&typeof prog.stationChats==='object'?prog.stationChats:{};
  state.stationTopics=prog.stationTopics&&typeof prog.stationTopics==='object'?prog.stationTopics:{};
  state.stationManifestEvents=prog.stationManifestEvents&&typeof prog.stationManifestEvents==='object'?prog.stationManifestEvents:{};
  state.stationAuditTrail=Array.isArray(prog.stationAuditTrail)?prog.stationAuditTrail.slice(-30):[];
  state.stationRetryMode=!!prog.stationRetryMode;state.stationThreat=clamp(Number(prog.stationThreat)||0,0,99);state.stationIncidentLogged=!!prog.stationIncidentLogged;state.stationFeedback=String(prog.stationFeedback||'').slice(0,500);
  state.stationComplete=!!prog.stationComplete;
  state.stationCorrect=clamp(Number(prog.stationCorrect)||0,0,6);
  state.stationProcessed=clamp(Number(prog.stationProcessed)||0,0,6);
  state.exploredRoomIds=Array.isArray(prog.exploredRoomIds)?prog.exploredRoomIds.slice(0,32):[];
  state.caseComparisons=Array.isArray(prog.caseComparisons)?prog.caseComparisons.slice(0,32):[];
  state.caseTheory=['mimic-timeline','storm-failure','staged-witness','duplicate-units'].includes(prog.caseTheory)?prog.caseTheory:'';
  state.theoryAttempts=clamp(Number(prog.theoryAttempts)||0,0,99);
  state.missingIds=Array.isArray(prog.missingIds)?prog.missingIds.slice(0,100):[];
  state.roomItemStates=prog.roomItemStates&&typeof prog.roomItemStates==='object'?prog.roomItemStates:{};
  state.disappearanceLog=Array.isArray(prog.disappearanceLog)?prog.disappearanceLog.slice(-100):[];
  state.exploredRooms=clamp(Number(prog.exploredRooms)||0,0,99);
  state.kills=clamp(Number(prog.kills)||0,0,999);
  state.shots=clamp(Number(prog.shots)||0,0,99999);
  state.anchorsDestroyed=Array.isArray(prog.anchorsDestroyed)?prog.anchorsDestroyed.slice(0,12):[];
  state.anchorsDisabled=!!prog.anchorsDisabled;state.trueEnding=!!prog.trueEnding;
  state.helpCount=clamp(Number(prog.helpCount)||0,0,999);
  state.huntsSurvived=clamp(Number(prog.huntsSurvived)||0,0,99);
  state.threatTier=clamp(Number(prog.threatTier)||0,0,6);
  state.extractionStarted=!!prog.extractionStarted;state.extractionHold=clamp(Number(prog.extractionHold)||0,0,30);
  state.extractionWave1=!!prog.extractionWave1;state.extractionWave2=!!prog.extractionWave2;state.extractionWave3=!!prog.extractionWave3;state.extractionWave4=!!prog.extractionWave4;
  caseRecords=Array.isArray(snapshot.caseRecords)?snapshot.caseRecords.slice(0,100):[];
  evidence=collectedClueCount();
  const itemObjectMap=new Map((Array.isArray(snapshot.objects)?snapshot.objects:[]).map(o=>[String(o.id),o]));
  for(const object of objects){const saved=itemObjectMap.get(String(object.id));if(saved){object.found=!!saved.found;object.missing=!!saved.missing;}}
  const survivorMap=new Map((Array.isArray(snapshot.survivors)?snapshot.survivors:[]).map(o=>[String(o.id),o]));
  for(const survivor of survivors){const saved=survivorMap.get(String(survivor.id));if(saved){survivor.found=!!saved.found;survivor.following=!!saved.following;survivor.delivered=!!saved.delivered;survivor.hp=clamp(Number(saved.hp)||1,0,1);survivor.x=clamp(Number(saved.x)||survivor.x,0,WORLD.w);survivor.y=clamp(Number(saved.y)||survivor.y,0,WORLD.h);}}
  if(snapshot.floor==='inside'&&/^(checkpoint|station|gas|cabin|tower|motel|diner|clinic|depot|church|warehouse|farmhouse)$/.test(String(snapshot.roomId||''))){
    state.floor='inside';state.room=makeRoom(String(snapshot.roomId));
  }else{state.floor='outside';state.room=null;}
  if(snapshot.player&&player){
    const maxX=state.floor==='inside'&&state.room?state.room.w:WORLD.w;
    const maxY=state.floor==='inside'&&state.room?state.room.h:WORLD.h;
    player.x=clamp(Number(snapshot.player.x)||520,20,maxX-20);player.y=clamp(Number(snapshot.player.y)||500,20,maxY-20);
    player.angle=clamp(Number(snapshot.player.angle)||0,-Math.PI*10,Math.PI*10);
    player.hp=clamp(Number(snapshot.player.hp)||player.maxHp,1,player.maxHp);player.stamina=clamp(Number(snapshot.player.stamina)||player.maxStamina,0,player.maxStamina);
    health=player.hp;stamina=player.stamina;
  }
  ammo=clamp(Number(inv.ammo)||0,0,99);reserve=clamp(Number(inv.reserve)||0,0,999);medkits=clamp(Number(inv.medkits)||0,0,20);batteryCells=clamp(Number(inv.batteryCells)||0,0,40);flashlightBattery=clamp(Number(inv.flashlightBattery)||0,0,100);flashlight=inv.flashlight!==false;
  state.running=true;state.paused=false;state.gameOver=false;state.won=false;state.prologueStage='swamp';
  document.body.classList.add('game-active');document.body.classList.remove('prologue-mode','prologue-call','prologue-drive','prologue-arrival');
  $('hud').style.display='block';setScreen('game');state.lastFrame=performance.now();camera.x=clamp(player.x-W/2,0,WORLD.w-W);camera.y=clamp(player.y-H/2,0,WORLD.h-H);lastSafe={x:player.x,y:player.y};
  updateHUD();updateObjectives();updateInventory();
}
async function cloudLoadGame(){
  if(!cloudAccount){cloudMessage('Sign in before loading a cloud save.','error');return;}
  const slot=$('cloudSaveSlot').value;
  try{
    const result=await cloudRequest('/api/saves/'+encodeURIComponent(slot));
    if(!result.save)throw new Error('No save exists in that slot.');
    cloudCloseAccount();
    restoreCloudSnapshot(result.save.payload);
    cloudMessage('Cloud save loaded. The patrol has resumed.','good');
  }catch(error){cloudMessage(error.message,'error');}
}
async function cloudRefreshAchievements(){
  if(!cloudAccount){$('cloudAchievementList').textContent='Sign in to sync achievements.';return;}
  try{
    const result=await cloudRequest('/api/achievements');
    const list=$('cloudAchievementList');list.replaceChildren();
    for(const item of result.achievements||[]){
      const row=document.createElement('div');row.className='account-row';
      const title=document.createElement('strong');title.textContent=(item.unlocked?'✓ UNLOCKED · ':'LOCKED · ')+item.title;
      const desc=document.createElement('div');desc.textContent=item.description;
      row.append(title,desc);list.appendChild(row);
    }
  }catch(error){$('cloudAchievementList').textContent=error.message;}
}
async function cloudRefreshLeaderboard(){
  try{
    const result=await cloudRequest('/api/leaderboard');
    const list=$('cloudLeaderboardList');list.replaceChildren();
    if(!result.entries.length){list.textContent='No completed runs have been recorded yet.';return;}
    result.entries.forEach((item,index)=>{
      const row=document.createElement('div');row.className='account-row';
      const title=document.createElement('strong');title.textContent='#'+(index+1)+' '+item.username+' · '+Number(item.score||0).toLocaleString()+' pts';
      const sub=document.createElement('div');sub.textContent=(item.trueEnding?'TRUE ENDING':'STANDARD ENDING')+' · '+Math.floor((Number(item.duration)||0)/60)+'m '+Math.floor((Number(item.duration)||0)%60)+'s';
      row.append(title,sub);list.appendChild(row);
    });
  }catch(error){$('cloudLeaderboardList').textContent=error.message;}
}
async function cloudRefreshStaffOverview(){
  if(!cloudAccount||cloudAccount.role!=='staff')return;
  try{
    const r=await cloudRequest('/api/staff/overview');
    $('staffOverview').textContent='STAFF DATABASE OVERVIEW\nAccounts: '+r.users+' · Saves: '+r.saves+' · Completed runs: '+r.runs+' · Achievement awards: '+r.awards;
  }catch(error){$('staffOverview').textContent=error.message;}
}
async function cloudRefreshAll(quiet=false){
  cloudRequestBusy=true;
  try{
    const status=await cloudRequest('/api/cloud/status');
    if(!status.configured){cloudMessage('MongoDB is not configured on the server. Add MONGODB_URI, MONGODB_DB_NAME, FLASK_SECRET_KEY, STAFF_USERNAME, and STAFF_PASSWORD in Render Environment. Local gameplay still works.','error');cloudSetIdentity(null);await cloudRefreshLeaderboard();return;}
    if(!quiet)cloudMessage(status.connected?'MongoDB connected.':'MongoDB connection check failed.');
    const account=await cloudRequest('/api/auth/me');
    cloudSetIdentity(account.user||null);
    if(cloudAccount){await cloudRefreshSaves();await cloudRefreshAchievements();if(cloudAccount.role==='staff')await cloudRefreshStaffOverview();}
    else{$('cloudSaveList').textContent='Sign in to view cloud saves.';$('cloudAchievementList').textContent='Sign in to sync achievements.';}
    await cloudRefreshLeaderboard();
    if(!quiet)cloudMessage(cloudAccount?'Cloud profile ready.':'Database ready. Sign in or create a player account.','good');
  }catch(error){cloudMessage(error.message,'error');}
  finally{cloudRequestBusy=false;}
}
async function cloudSubmitRun(success){
  if(!cloudAccount)return;
  try{
    const stats=cloudStats();stats.won=!!success;
    const route=success?'/api/runs/complete':'/api/progress';
    const result=await cloudRequest(route,{method:'POST',body:{stats}});
    if(success)toast('CLOUD RECORD SAVED · SCORE '+Number(result.score||0).toLocaleString(),3.1);
  }catch(error){console.warn('Cloud progress sync:',error.message);}
}

function bindEvents(){
  $('accountBtn').addEventListener('click',()=>cloudOpenAccount('menu'));
  $('pauseAccount').addEventListener('click',()=>cloudOpenAccount('pause'));
  $('backAccount').addEventListener('click',cloudCloseAccount);
  $('accountForm').addEventListener('submit',cloudLogin);
  $('accountRegister').addEventListener('click',cloudRegister);
  $('accountLogout').addEventListener('click',cloudLogout);
  $('cloudSaveButton').addEventListener('click',cloudSaveGame);
  $('cloudLoadButton').addEventListener('click',cloudLoadGame);
  $('cloudRefreshSaves').addEventListener('click',cloudRefreshSaves);
  $('cloudRefreshLeaderboard').addEventListener('click',cloudRefreshLeaderboard);
  $('refreshStaffOverview').addEventListener('click',cloudRefreshStaffOverview);
  const partnerComposer=$('partnerComposer');
  if(partnerComposer)partnerComposer.addEventListener('submit',e=>{e.preventDefault();sendPartnerChat();});
  $('radioBreachPanel').addEventListener('click',e=>{const choice=e.target.closest('[data-radio-breach-choice]');if(choice)resolveRadioBreach(choice.dataset.radioBreachChoice);});
  $('start').addEventListener('click',()=>{audioStart();resetGame();});
  $('characterBtn').addEventListener('click',()=>{
    state.pendingCharacter=state.selectedCharacter;
    setScreen('character');
    updateCharacterSelection();
  });
  $('controlsBtn').addEventListener('click',()=>{
    state.pendingMode=state.controlMode;
    applyControlMode();
    setScreen('controls');
  });
  $('howBtn').addEventListener('click',()=>setScreen('how'));
  $('creditsBtn').addEventListener('click',()=>setScreen('credits'));
  $('backCharacter').addEventListener('click',()=>setScreen('menu'));
  $('confirmCharacter').addEventListener('click',()=>{
    state.selectedCharacter=state.pendingCharacter;
    setScreen('menu');
    toast('PERSONNEL FILE UPDATED: '+specs[state.selectedCharacter].name.toUpperCase(),1.6);
  });
  for(const btn of document.querySelectorAll('[data-char]')){
    btn.addEventListener('click',()=>{
      state.pendingCharacter=btn.dataset.char;
      updateCharacterSelection();
      tone(420,.07,'sine',.06,70);
    });
  }
  $('desktopMode').addEventListener('click',()=>{state.pendingMode='desktop';applyControlMode();});
  $('mobileMode').addEventListener('click',()=>{state.pendingMode='mobile';applyControlMode();});
  $('saveControls').addEventListener('click',()=>{
    state.controlMode=state.pendingMode;
    applyControlMode();
    setScreen('menu');
    toast('CONTROL MODE SAVED: '+state.controlMode.toUpperCase(),1.7);
  });
  $('backControls').addEventListener('click',()=>setScreen('menu'));
  $('backHow').addEventListener('click',()=>setScreen('menu'));
  $('backCredits').addEventListener('click',()=>setScreen('menu'));
  $('disclaimerBtn').addEventListener('click',()=>{
    $('enablePersonalScares').checked=state.options.personalScares;
    $('enableVoiceWhispers').checked=state.options.voiceWhispers;
    $('disclaimerPanel').classList.remove('hidden');
  });
  $('dismissDisclaimer').addEventListener('click',()=>{
    state.options.personalScares=$('enablePersonalScares').checked;
    state.options.voiceWhispers=$('enableVoiceWhispers').checked;
    $('disclaimerPanel').classList.add('hidden');
    toast(state.options.voiceWhispers?'VOICE WHISPERS ENABLED. THE RADIO MAY LIE.':'VOICE WHISPERS DISABLED.',1.8);
  });
  $('enablePersonalScares').addEventListener('change',e=>state.options.personalScares=e.target.checked);
  $('enableVoiceWhispers').addEventListener('change',e=>state.options.voiceWhispers=e.target.checked);
  $('objectiveToggle').addEventListener('click',openObjectives);
  $('closeObjectives').addEventListener('click',closeOverlay);
  $('closeMemorial').addEventListener('click',closeOverlay);
  $('evidenceBoard').addEventListener('click',e=>{
    const button=e.target.closest('[data-study-id]');
    if(button)studyEvidence(button.dataset.studyId);
  });
  $('compareEvidence').addEventListener('click',compareEvidence);
  $('theoryChoices').addEventListener('click',e=>{
    const button=e.target.closest('[data-theory]');
    if(button)selectCaseTheory(button.dataset.theory);
  });
  $('submitTheory').addEventListener('click',submitCaseTheory);
  $('interviewChoices').addEventListener('click',e=>{
    const button=e.target.closest('[data-witness-choice]');
    if(button)answerWitness(Number(button.dataset.witnessChoice));
  });
  $('interviewContinue').addEventListener('click',continueWitnessInterview);
  $('endInterview').addEventListener('click',finishWitnessInterview);
  $('stationComposer').addEventListener('submit',e=>{e.preventDefault();sendStationChat();});
  $('stationZoomInterview').addEventListener('click',openSuspectZoom);
  $('closeSuspectZoom').addEventListener('click',closeSuspectZoom);
  $('suspectZoomPanel').addEventListener('click',e=>{
    const choice=e.target.closest('[data-suspect-choice]');
    if(choice)handleSuspectZoomChoice(choice.dataset.suspectChoice);
  });
  $('stationIntakePanel').addEventListener('click',e=>{
    const ask=e.target.closest('[data-station-ask]');
    const topic=e.target.closest('[data-station-topic]');
    const decision=e.target.closest('[data-station-decision]');
    if(ask)stationInspect(ask.dataset.stationAsk);
    if(topic)stationAskTopic(topic.dataset.stationTopic);
    if(decision)stationRecordDecision(decision.dataset.stationDecision);
  });
  $('stationNextVisitor').addEventListener('click',stationNextVisitor);
  $('stationReviewFiles').addEventListener('click',reviewStationFiles);
  $('stationClose').addEventListener('click',closeOverlay);
  $('leaveInterview').addEventListener('click',()=>{
    toast('INTERVIEW INTERRUPTED. SILAS MAY NOT WAIT FOR ANOTHER CHANCE.',2.8);
    closeOverlay();
  });
  $('closeInventory').addEventListener('click',closeOverlay);
  $('useMed').addEventListener('click',useMedkit);
  $('resume').addEventListener('click',closeOverlay);
  $('pauseObjectives').addEventListener('click',()=>{
    updateObjectives();
    setScreen('objectives');
  });
  $('pauseMenu').addEventListener('click',()=>{
    state.gameOver=true;
    state.running=false;
    $('hud').style.display='none';
    document.body.classList.remove('game-active');
    setScreen('menu');
  });
  $('again').addEventListener('click',()=>{audioStart();resetGame();});
  $('toMenu').addEventListener('click',()=>{
    $('hud').style.display='none';
    document.body.classList.remove('game-active');
    setScreen('menu');
  });
  $('closeRadio').addEventListener('click',closeOverlay);
  $('hideAction').addEventListener('click',toggleHide);
  $('screamAction').addEventListener('click',playerScream);
  $('helpAction').addEventListener('click',callPartnerForHelp);
  $('touchInteract').addEventListener('pointerdown',e=>{e.preventDefault();interact();});
  $('touchShoot').addEventListener('pointerdown',e=>{e.preventDefault();shoot();});
  $('touchLight').addEventListener('pointerdown',e=>{e.preventDefault();toggleFlashlight();});
  $('touchReload').addEventListener('pointerdown',e=>{e.preventDefault();reloadWeapon();});
  $('touchRun').addEventListener('pointerdown',e=>{e.preventDefault();touchRun=true;});
  for(const eventName of ['pointerup','pointercancel','pointerleave'])$('touchRun').addEventListener(eventName,()=>touchRun=false);
  $('touchBag').addEventListener('pointerdown',e=>{e.preventDefault();openInventory();});
  const directionIds={up:'w',down:'s',left:'a',right:'d'};
  for(const [id,key] of Object.entries(directionIds)){
    const btn=$(id);
    btn.addEventListener('pointerdown',e=>{e.preventDefault();keys[key]=true;btn.setPointerCapture(e.pointerId);});
    for(const eventName of ['pointerup','pointercancel','pointerleave'])btn.addEventListener(eventName,()=>keys[key]=false);
  }
  canvas.addEventListener('pointermove',e=>{
    const rect=canvas.getBoundingClientRect();
    pointer.x=e.clientX-rect.left;
    pointer.y=e.clientY-rect.top;
  });
  canvas.addEventListener('pointerdown',e=>{
    if(state.prologueStage==='call'){acceptDispatch();return;}
    if(state.prologueStage==='arrival'){enterNightSearch();return;}
    if(state.prologueStage==='drive')return;
    if(state.controlMode==='desktop'&&e.button===0){
      pointer.down=true;
      shoot();
    }
  });
  window.addEventListener('pointerup',()=>pointer.down=false);
  canvas.addEventListener('contextmenu',e=>e.preventDefault());
  window.addEventListener('keydown',onKeyDown);
  window.addEventListener('keyup',onKeyUp);
  window.addEventListener('blur',()=>{
    keys={};
    pointer.down=false;
    touchRun=false;
    if(state.running)pauseGame();
  });
  document.addEventListener('visibilitychange',()=>{
    if(document.hidden&&state.running)pauseGame();
  });
}
function updateCharacterSelection(){
  for(const btn of document.querySelectorAll('[data-char]'))btn.classList.toggle('selected',btn.dataset.char===state.pendingCharacter);
  const spec=specs[state.pendingCharacter];
  const messages={
    hugo:'Boy character. Officer Hugo is a dependable male state trooper with balanced speed, health, and stamina.',
    yumi:'Girl character. Officer Yumi is a quick female investigator with faster movement and longer stamina.'
  };
  $('characterDetails').innerHTML='<b>'+(state.pendingCharacter==='hugo'?'BOY · ':'GIRL · ')+escapeHTML(spec.name.toUpperCase())+'</b><br>'+escapeHTML(messages[state.pendingCharacter])+'<br><br>Speed: '+spec.speed+' · Max health: '+spec.hp+' · Starting ammo: '+spec.ammo+' + '+spec.reserve+' spare';
}
function toggleFlashlight(){
  if(state.hideSpotActive){toast('KEEP THE FLASHLIGHT DARK WHILE HIDING. LEAVE COVER BEFORE USING IT.',2.0);return;}
  if(flashlightBattery<=0){toast('FLASHLIGHT BATTERY EMPTY. SEARCH FOR CELLS.');return;}
  flashlight=!flashlight;
  if(flashlight)state.adaptiveHorror.flashlightExposure=Math.max(0,state.adaptiveHorror.flashlightExposure);
  sound('radio');
  toast(flashlight?'FLASHLIGHT ON. STAY ALERT.':'FLASHLIGHT OFF. MOVE QUIETLY.',1.3);
}
function onKeyDown(e){
  if(e.target&&e.target.id==='partnerInput'){
    if(e.key==='Enter'){e.preventDefault();sendPartnerChat();}
    if(e.key==='Escape'){e.preventDefault();e.target.blur();}
    return;
  }
  if(e.target&&e.target.id==='stationChatInput'){
    if(e.key==='Enter'){e.preventDefault();sendStationChat();}
    if(e.key==='Escape'){e.preventDefault();e.target.blur();}
    return;
  }
  if(e.target&&['accountUsername','accountPassword'].includes(e.target.id)){
    if(e.key==='Escape'){e.preventDefault();e.target.blur();}
    return;
  }
  const key=e.key.toLowerCase();
  if(state.radioIncidentActive&&key==='escape'){e.preventDefault();resolveRadioBreach('silence');return;}
  keys[key]=true;
  if([' ','arrowup','arrowdown','arrowleft','arrowright'].includes(key))e.preventDefault();
  if(e.repeat)return;
  if(key==='escape'){
    if(state.screen==='game')pauseGame();
    else if(['objectives','inventory','radio','memorial'].includes(state.screen))closeOverlay();
    else if(state.screen==='account')cloudCloseAccount();
    else if(state.screen==='pause')closeOverlay();
    else if(state.screen!=='menu')setScreen('menu');
    return;
  }
  if(!state.running)return;
  if(state.prologueStage==='call'&&(key==='e'||key==='enter')){acceptDispatch();return;}
  if(state.prologueStage==='arrival'&&(key==='e'||key==='enter')){enterNightSearch();return;}
  if(key==='e')interact();
  if(key==='c')toggleHide();
  if(key==='g')playerScream();
  if(key==='h')callPartnerForHelp();
  if(key==='f')toggleFlashlight();
  if(key==='r'){
    state.reloadActive=true;
    reloadWeapon();
  }
  if(key==='j'||key==='tab'){
    e.preventDefault();
    openObjectives();
  }
  if(key==='i')openInventory();
  if(key===' '&&state.floor==='outside')shoot();
  if(key==='q'){
    if(batteryCells>0){
      batteryCells--;
      flashlightBattery=Math.min(100,flashlightBattery+55);
      toast('BATTERY CELL USED. LIGHT RESTORED.',1.5);
      updateHUD();
      updateInventory();
    }else toast('NO BATTERY CELLS LEFT.',1.2);
  }
}
function onKeyUp(e){
  keys[e.key.toLowerCase()]=false;
}
function menuFrame(){
  if(state.running)return;
  drawMenuArt();
  requestAnimationFrame(menuFrame);
}
function loop(now){
  if(!state.running)return;
  if(document.hidden){state.lastFrame=now;requestAnimationFrame(loop);return;}
  const dt=Math.min(.035,Math.max(.001,(now-state.lastFrame)/1000));
  state.lastFrame=now;
  if(!state.paused&&!state.gameOver)update(dt);
  drawWorld();
  if(state.running)requestAnimationFrame(loop);
}
function boot(){
  initializeAssets();
  drawPortraits();
  drawMenuArt();
  bindEvents();
  applyControlMode();
  updateCharacterSelection();
  updateObjectives();
  menuFrame();
}
boot();
})();
</script>
</body>
</html>'''

class DatabaseUnavailable(RuntimeError):
    pass

_mongo_client = None
_mongo_database = None
_mongo_indexes_ready = False
_staff_bootstrap_ready = False

ACHIEVEMENT_CATALOG = {
    'first_trace': {'title':'First Trace','description':'Recover your first physical clue.'},
    'forensic_analyst': {'title':'Forensic Analyst','description':'Study six pieces of evidence.'},
    'timeline_breaker': {'title':'Timeline Breaker','description':'Submit the supported mimic-timeline theory after four reports.'},
    'night_intake': {'title':'Night Intake','description':'Complete the six-visitor police station audit.'},
    'two_out_alive': {'title':'Two Out Alive','description':'Find both missing people.'},
    'nightmare_survivor': {'title':'Nightmare Survivor','description':'Complete the extraction and escape the night.'},
    'signal_silencer': {'title':'Signal Silencer','description':'Destroy all three signal anchors and complete the true ending.'},
    'smiler_endurance': {'title':'Smiler Endurance','description':'Survive three hunts and escape.'}
}


def utc_now():
    return datetime.now(timezone.utc)


def _is_mongo_ready():
    return bool(os.environ.get('MONGODB_URI', '').strip()) and MongoClient is not None


def get_database():
    global _mongo_client, _mongo_database, _mongo_indexes_ready
    uri = os.environ.get('MONGODB_URI', '').strip()
    if not uri:
        raise DatabaseUnavailable('MongoDB is not configured. Add MONGODB_URI to the server environment.')
    if MongoClient is None:
        raise DatabaseUnavailable('MongoDB driver is not installed. Add pymongo[srv] to requirements.txt and redeploy.')
    if _mongo_database is None:
        try:
            _mongo_client = MongoClient(uri, serverSelectionTimeoutMS=4500, connectTimeoutMS=4500, appname='FloridaShadows')
            _mongo_client.admin.command('ping')
            database_name = os.environ.get('MONGODB_DB_NAME', 'florida_shadows').strip() or 'florida_shadows'
            _mongo_database = _mongo_client[database_name]
        except Exception as exc:
            _mongo_client = None
            _mongo_database = None
            raise DatabaseUnavailable('Could not connect to MongoDB. Check MONGODB_URI, network access, and Atlas database-user permissions.') from exc
    if not _mongo_indexes_ready:
        try:
            _mongo_database.users.create_index([('username_key', ASCENDING)], unique=True)
            _mongo_database.users.create_index([('uid', ASCENDING)], unique=True)
            _mongo_database.saves.create_index([('user_id', ASCENDING), ('slot', ASCENDING)], unique=True)
            _mongo_database.saves.create_index([('user_id', ASCENDING), ('updated_at', DESCENDING)])
            _mongo_database.leaderboard.create_index([('score', DESCENDING), ('completed_at', ASCENDING)])
            _mongo_database.achievements.create_index([('user_id', ASCENDING), ('achievement_id', ASCENDING)], unique=True)
            _mongo_indexes_ready = True
        except Exception as exc:
            raise DatabaseUnavailable('MongoDB connected but could not create required indexes. Check the database user permissions.') from exc
    ensure_staff_account(_mongo_database)
    return _mongo_database


def ensure_staff_account(db):
    global _staff_bootstrap_ready
    if _staff_bootstrap_ready:
        return
    username = os.environ.get('STAFF_USERNAME', '').strip()
    password = os.environ.get('STAFF_PASSWORD', '')
    if not username or not password:
        return
    if not re.fullmatch(r'[A-Za-z0-9_.-]{3,24}', username) or len(password) < 10:
        raise DatabaseUnavailable('STAFF_USERNAME must be 3–24 valid characters and STAFF_PASSWORD must be at least 10 characters.')
    key = username.casefold()
    try:
        user = db.users.find_one({'username_key': key})
        pass_hash = generate_password_hash(password)
        if user:
            db.users.update_one({'_id': user['_id']}, {'$set': {'username': username, 'username_key': key, 'password_hash': pass_hash, 'role': 'staff', 'updated_at': utc_now()}})
        else:
            db.users.insert_one({'uid': secrets.token_urlsafe(24), 'username': username, 'username_key': key, 'password_hash': pass_hash, 'role': 'staff', 'created_at': utc_now(), 'last_login_at': None})
        _staff_bootstrap_ready = True
    except PyMongoError as exc:
        raise DatabaseUnavailable('Could not initialize the staff account in MongoDB. Check staff environment variables and database permissions.') from exc


def api_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def safe_json_value(value, depth=0):
    if depth > 8:
        return None
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return max(-1000000000, min(1000000000, value))
    if isinstance(value, float):
        if not math.isfinite(value):
            return 0
        return max(-1000000000, min(1000000000, value))
    if isinstance(value, str):
        return value[:1000]
    if isinstance(value, list):
        return [safe_json_value(item, depth + 1) for item in value[:250]]
    if isinstance(value, dict):
        result = {}
        for key, item in list(value.items())[:250]:
            if isinstance(key, str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,80}', key):
                result[key] = safe_json_value(item, depth + 1)
        return result
    return None


def validate_save_payload(raw):
    if not isinstance(raw, dict):
        raise ValueError('Save data is missing or invalid.')
    allowed = {'schemaVersion', 'selectedCharacter', 'floor', 'roomId', 'player', 'inventory', 'progress', 'survivors', 'objects', 'caseRecords'}
    payload = {key: safe_json_value(value) for key, value in raw.items() if key in allowed}
    if payload.get('selectedCharacter') not in ('hugo', 'yumi'):
        payload['selectedCharacter'] = 'hugo'
    payload['floor'] = 'inside' if payload.get('floor') == 'inside' else 'outside'
    if payload['floor'] == 'outside':
        payload['roomId'] = ''
    allowed_rooms = {'checkpoint','station','gas','cabin','tower','motel','diner','clinic','depot','church','warehouse','farmhouse'}
    if payload['floor'] == 'inside' and payload.get('roomId') not in allowed_rooms:
        raise ValueError('The saved room is invalid. Please save again from inside a valid building.')
    for key in ('player', 'inventory', 'progress'):
        if not isinstance(payload.get(key), dict):
            payload[key] = {}
    for key in ('survivors', 'objects', 'caseRecords'):
        if not isinstance(payload.get(key), list):
            payload[key] = []
    encoded = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    if len(encoded.encode('utf-8')) > 64000:
        raise ValueError('This save is too large. Reduce the number of recorded clues and retry.')
    return payload


def user_for_session(db):
    uid = session.get('user_uid')
    if not isinstance(uid, str) or not uid:
        return None
    user = db.users.find_one({'uid': uid}, {'password_hash': 0, 'username_key': 0})
    if not user:
        session.clear()
    return user


def public_user(user):
    if not user:
        return None
    return {'username': user.get('username', 'Player'), 'role': user.get('role', 'player'), 'createdAt': _date_iso(user.get('created_at'))}


def _date_iso(value):
    if not value:
        return None
    if isinstance(value, str):
        return value
    try:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat(timespec='minutes')
    except Exception:
        return None


def clean_stats(raw):
    raw = raw if isinstance(raw, dict) else {}
    def number(key, default=0, maximum=100000):
        try:
            value = float(raw.get(key, default))
            if not math.isfinite(value): return default
            return max(0, min(maximum, value))
        except (TypeError, ValueError):
            return default
    return {
        'cluesCollected': int(number('cluesCollected', 0, 100)),
        'cluesStudied': int(number('cluesStudied', 0, 100)),
        'crossReferences': int(number('crossReferences', 0, 100)),
        'caseTheory': str(raw.get('caseTheory', ''))[:50],
        'witnessInterviewed': bool(raw.get('witnessInterviewed')),
        'witnessTrust': number('witnessTrust', 0, 10),
        'stationComplete': bool(raw.get('stationComplete')),
        'stationCorrect': int(number('stationCorrect', 0, 6)),
        'stationProcessed': int(number('stationProcessed', 0, 6)),
        'survivors': int(number('survivors', 0, 2)),
        'survivorsDelivered': int(number('survivorsDelivered', 0, 2)),
        'keysFound': bool(raw.get('keysFound')),
        'buildingsSearched': int(number('buildingsSearched', 0, 32)),
        'extractionHold': number('extractionHold', 0, 30),
        'extractionSurvived': bool(raw.get('extractionSurvived')),
        'anchorsDestroyed': int(number('anchorsDestroyed', 0, 3)),
        'trueEnding': bool(raw.get('trueEnding')),
        'huntsSurvived': int(number('huntsSurvived', 0, 99)),
        'elapsed': number('elapsed', 0, 86400),
        'kills': int(number('kills', 0, 10000)),
        'shots': int(number('shots', 0, 100000)),
        'won': bool(raw.get('won'))
    }


def evaluate_achievements(db, user, stats):
    if not user:
        return
    rules = {
        'first_trace': stats['cluesCollected'] >= 1,
        'forensic_analyst': stats['cluesStudied'] >= 6,
        'timeline_breaker': stats['crossReferences'] >= 4 and stats['caseTheory'] == 'mimic-timeline',
        'night_intake': stats['stationComplete'] and stats['stationCorrect'] >= 5,
        'two_out_alive': stats['survivors'] >= 2,
        'nightmare_survivor': stats['won'] and stats['cluesStudied'] >= 6 and stats['survivorsDelivered'] >= 2 and stats['extractionHold'] >= 30,
        'signal_silencer': stats['won'] and stats['anchorsDestroyed'] >= 3 and stats['trueEnding'],
        'smiler_endurance': stats['won'] and stats['huntsSurvived'] >= 3
    }
    for achievement_id, unlocked in rules.items():
        if not unlocked:
            continue
        data = ACHIEVEMENT_CATALOG[achievement_id]
        db.achievements.update_one(
            {'user_id': user['uid'], 'achievement_id': achievement_id},
            {'$setOnInsert': {'username': user.get('username', 'Player'), 'title': data['title'], 'description': data['description'], 'unlocked_at': utc_now()}},
            upsert=True
        )


def json_error(message, status=400):
    return jsonify({'ok': False, 'error': message}), status


@app.errorhandler(DatabaseUnavailable)
def handle_database_unavailable(error):
    return jsonify({'ok': False, 'error': str(error)}), 503


@app.errorhandler(PyMongoError)
def handle_mongo_error(error):
    return jsonify({'ok': False, 'error': 'MongoDB is temporarily unavailable. Check the Atlas cluster status and retry.'}), 503


@app.get('/api/cloud/status')
def cloud_status():
    configured = bool(os.environ.get('MONGODB_URI', '').strip()) and MongoClient is not None
    if not configured:
        return jsonify({'configured': False, 'connected': False, 'driverInstalled': MongoClient is not None})
    try:
        db = get_database()
        db.command('ping')
        return jsonify({'configured': True, 'connected': True, 'database': os.environ.get('MONGODB_DB_NAME', 'florida_shadows')})
    except DatabaseUnavailable as exc:
        return jsonify({'configured': True, 'connected': False, 'error': str(exc)}), 503


@app.post('/api/auth/register')
def api_register():
    data = api_body()
    username = str(data.get('username', '')).strip()
    password = data.get('password', '')
    if not re.fullmatch(r'[A-Za-z0-9_.-]{3,24}', username):
        return json_error('Username must be 3–24 characters using letters, numbers, dot, underscore, or hyphen.')
    if not isinstance(password, str) or len(password) < 10 or len(password) > 128:
        return json_error('Password must be between 10 and 128 characters.')
    db = get_database()
    ensure_staff_account(db)
    key = username.casefold()
    if db.users.find_one({'username_key': key}):
        return json_error('That username is already registered. Choose another username or sign in.', 409)
    user = {'uid': secrets.token_urlsafe(24), 'username': username, 'username_key': key, 'password_hash': generate_password_hash(password), 'role': 'player', 'created_at': utc_now(), 'last_login_at': utc_now()}
    try:
        db.users.insert_one(user)
    except DuplicateKeyError:
        return json_error('That username is already registered. Choose another username or sign in.', 409)
    session.clear()
    session['user_uid'] = user['uid']
    return jsonify({'ok': True, 'user': public_user(user)})


@app.post('/api/auth/login')
def api_login():
    data = api_body()
    username = str(data.get('username', '')).strip()
    password = data.get('password', '')
    if not username or not isinstance(password, str) or len(password) > 128:
        return json_error('Enter your username and password.')
    db = get_database()
    ensure_staff_account(db)
    user = db.users.find_one({'username_key': username.casefold()})
    if not user or not check_password_hash(user.get('password_hash', ''), password):
        return json_error('Invalid username or password.', 401)
    db.users.update_one({'_id': user['_id']}, {'$set': {'last_login_at': utc_now()}})
    session.clear()
    session['user_uid'] = user['uid']
    return jsonify({'ok': True, 'user': public_user(user)})


@app.post('/api/auth/logout')
def api_logout():
    session.clear()
    return jsonify({'ok': True})


@app.get('/api/auth/me')
def api_me():
    db = get_database()
    user = user_for_session(db)
    return jsonify({'ok': True, 'user': public_user(user), 'database': True})


@app.route('/api/saves', methods=['GET', 'POST'])
def api_saves():
    db = get_database()
    user = user_for_session(db)
    if not user:
        return json_error('Sign in to use cloud saves.', 401)
    if request.method == 'GET':
        docs = list(db.saves.find({'user_id': user['uid']}, {'payload': 0}).sort('updated_at', DESCENDING).limit(3))
        saves = []
        for doc in docs:
            stats = clean_stats((doc.get('payload') or {}).get('progress', {}).get('gameStats', {}))
            saves.append({'slot': doc.get('slot'), 'character': (doc.get('payload') or {}).get('selectedCharacter', 'hugo'), 'updatedAt': _date_iso(doc.get('updated_at')), 'cluesStudied': stats['cluesStudied'], 'survivors': stats['survivors']})
        return jsonify({'ok': True, 'saves': saves})
    data = api_body()
    slot = str(data.get('slot', ''))
    if slot not in ('slot-1', 'slot-2', 'slot-3'):
        return json_error('Choose save slot 1, 2, or 3.')
    try:
        payload = validate_save_payload(data.get('payload'))
    except ValueError as exc:
        return json_error(str(exc))
    now = utc_now()
    db.saves.update_one({'user_id': user['uid'], 'slot': slot}, {'$set': {'username': user['username'], 'payload': payload, 'updated_at': now}, '$setOnInsert': {'created_at': now}}, upsert=True)
    stats = clean_stats((payload.get('progress') or {}).get('gameStats', {}))
    evaluate_achievements(db, user, stats)
    db.users.update_one({'uid': user['uid']}, {'$set': {'last_seen_at': now, 'latest_progress': {'cluesStudied': stats['cluesStudied'], 'survivors': stats['survivors'], 'elapsed': stats['elapsed']}}})
    return jsonify({'ok': True, 'slot': slot, 'updatedAt': _date_iso(now)})


@app.get('/api/saves/<slot>')
def api_load_save(slot):
    if slot not in ('slot-1', 'slot-2', 'slot-3'):
        return json_error('Unknown save slot.')
    db = get_database()
    user = user_for_session(db)
    if not user:
        return json_error('Sign in to load cloud saves.', 401)
    doc = db.saves.find_one({'user_id': user['uid'], 'slot': slot}, {'_id': 0, 'user_id': 0})
    if not doc:
        return jsonify({'ok': True, 'save': None})
    return jsonify({'ok': True, 'save': {'slot': doc.get('slot'), 'updatedAt': _date_iso(doc.get('updated_at')), 'payload': doc.get('payload')}})


@app.delete('/api/saves/<slot>')
def api_delete_save(slot):
    if slot not in ('slot-1', 'slot-2', 'slot-3'):
        return json_error('Unknown save slot.')
    db = get_database()
    user = user_for_session(db)
    if not user:
        return json_error('Sign in to delete cloud saves.', 401)
    result = db.saves.delete_one({'user_id': user['uid'], 'slot': slot})
    return jsonify({'ok': True, 'deleted': result.deleted_count > 0})


@app.get('/api/leaderboard')
def api_leaderboard():
    db = get_database()
    docs = list(db.leaderboard.find({}, {'_id': 0, 'user_id': 0}).sort([('score', DESCENDING), ('completed_at', ASCENDING)]).limit(25))
    entries = []
    for rank, doc in enumerate(docs, 1):
        entries.append({'rank': rank, 'username': doc.get('username', 'Unknown officer'), 'score': int(doc.get('score', 0)), 'duration': int(doc.get('duration', 0)), 'trueEnding': bool(doc.get('true_ending')), 'completedAt': _date_iso(doc.get('completed_at'))})
    return jsonify({'ok': True, 'entries': entries})


@app.get('/api/achievements')
def api_achievements():
    db = get_database()
    user = user_for_session(db)
    if not user:
        return json_error('Sign in to sync achievements.', 401)
    unlocked = {d['achievement_id'] for d in db.achievements.find({'user_id': user['uid']}, {'achievement_id': 1})}
    achievements = []
    for achievement_id, item in ACHIEVEMENT_CATALOG.items():
        achievements.append({'id': achievement_id, 'title': item['title'], 'description': item['description'], 'unlocked': achievement_id in unlocked})
    return jsonify({'ok': True, 'achievements': achievements})


@app.post('/api/progress')
def api_progress():
    data = api_body()
    db = get_database()
    user = user_for_session(db)
    if not user:
        return json_error('Sign in to sync progress.', 401)
    stats = clean_stats(data.get('stats'))
    evaluate_achievements(db, user, stats)
    db.users.update_one({'uid': user['uid']}, {'$set': {'last_seen_at': utc_now(), 'latest_progress': stats}})
    return jsonify({'ok': True})


@app.post('/api/runs/complete')
def api_complete_run():
    data = api_body()
    db = get_database()
    user = user_for_session(db)
    if not user:
        return json_error('Sign in to record a completed run.', 401)
    stats = clean_stats(data.get('stats'))
    valid = (
        stats['won'] and stats['cluesCollected'] >= 6 and stats['cluesStudied'] >= 6 and
        stats['crossReferences'] >= 4 and stats['caseTheory'] == 'mimic-timeline' and
        stats['witnessInterviewed'] and stats['witnessTrust'] >= 2 and
        stats['stationComplete'] and stats['stationCorrect'] >= 5 and
        stats['survivorsDelivered'] >= 2 and stats['keysFound'] and
        stats['buildingsSearched'] >= 5 and stats['extractionHold'] >= 30
    )
    if not valid:
        evaluate_achievements(db, user, stats)
        db.users.update_one({'uid': user['uid']}, {'$set': {'last_seen_at': utc_now(), 'latest_progress': stats}})
        return json_error('The run did not satisfy the full escape conditions; no leaderboard entry was added.', 409)
    seconds = int(stats['elapsed'])
    score = int(max(0, min(999999, 10000 + stats['cluesStudied'] * 250 + stats['crossReferences'] * 200 + stats['survivorsDelivered'] * 1000 + stats['anchorsDestroyed'] * 500 + stats['kills'] * 35 + stats['huntsSurvived'] * 150 - seconds * 2)))
    now = utc_now()
    db.leaderboard.insert_one({'user_id': user['uid'], 'username': user['username'], 'score': score, 'duration': seconds, 'true_ending': bool(stats['trueEnding'] and stats['anchorsDestroyed'] >= 3), 'completed_at': now, 'stats': stats})
    evaluate_achievements(db, user, stats)
    db.users.update_one({'uid': user['uid']}, {'$set': {'last_seen_at': now, 'latest_progress': stats, 'best_score': max(int(user.get('best_score', 0)), score)}})
    return jsonify({'ok': True, 'score': score, 'completedAt': _date_iso(now)})


@app.get('/api/staff/overview')
def api_staff_overview():
    db = get_database()
    user = user_for_session(db)
    if not user:
        return json_error('Sign in with your staff account to view this page.', 401)
    if user.get('role') != 'staff':
        return json_error('Staff access required.', 403)
    return jsonify({'ok': True, 'users': db.users.count_documents({}), 'saves': db.saves.count_documents({}), 'runs': db.leaderboard.count_documents({}), 'awards': db.achievements.count_documents({})})


@app.get('/')
def index():
    return Response(HTML, mimetype='text/html')

@app.get('/health')
def health():
    return jsonify(status='ok', game='Florida Shadows: The Living Nightmare', version='MongoDB Cloud Edition', mongodb_configured=bool(os.environ.get('MONGODB_URI', '').strip()))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5000'))
    app.run(host='0.0.0.0', port=port, debug=False)
