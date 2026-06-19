import { useEffect, useRef } from 'react';

const TILT = 0.28;
const COLORS = ['#FFD264', '#E8952A', '#C8701E', '#FFFFFF'];

function hexToRgb(hex) {
  if (hex === '#FFFFFF') return '255,255,255';
  return [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
  ].join(',');
}

const STATE_CONFIG = {
  idle:       { nameRgb: '232,213,163' },
  listening:  { nameRgb: '255,210,100' },
  processing: { nameRgb: '255,160,60'  },
  responding: { nameRgb: '232,200,120' },
};

export default function BlackHole({ alfredState }) {
  const canvasRef = useRef(null);
  const stateRef = useRef(alfredState);
  const animRef = useRef(null);

  useEffect(() => {
    stateRef.current = alfredState;
  }, [alfredState]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const CX = canvas.width / 2;
    const CY = canvas.height / 2;

    const particles = Array.from({ length: 150 }, () => {
      const radius = 100 + Math.random() * 160;
      return {
        angle: Math.random() * Math.PI * 2,
        radius,
        angularVelocity: (0.002 + Math.random() * 0.006) * (radius < 160 ? 1.5 : 1),
        size: 1 + Math.random() * 1.5,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        opacity: 0.4 + Math.random() * 0.6,
        trail: [],
        hasTrail: Math.random() < 0.2,
      };
    });

    const ringRots = Array.from({ length: 70 }, () => Math.random() * Math.PI * 2);
    let ripples = [];
    let lastRipple = 0;
    const startTime = performance.now();

    function drawFrame(now) {
      const state = stateRef.current;
      const t = (now - startTime) / 1000;
      const diskOpacity = state === 'idle' ? 0.6 : state === 'processing' ? 1.0 : state === 'listening' ? 0.9 : 0.7;
      const speedMult = state === 'listening' ? 1.5 : state === 'processing' ? 2.2 : state === 'responding' ? 0.8 : 1.0;
      const pSpeed = state === 'processing' ? 2.5 : state === 'listening' ? 1.8 : state === 'responding' ? 0.7 : 1.0;
      const breathe = state === 'idle' ? 0.05 * Math.sin(t * (Math.PI * 2 / 4)) : 0;

      const shake = state === 'processing'
        ? { x: (Math.random() - 0.5) * 2, y: (Math.random() - 0.5) * 2 }
        : { x: 0, y: 0 };

      ctx.save();
      ctx.translate(shake.x, shake.y);

      ctx.fillStyle = '#050507';
      ctx.fillRect(-2, -2, canvas.width + 4, canvas.height + 4);

      ctx.save();
      ctx.shadowBlur = 80; ctx.shadowColor = 'rgba(30,60,90,0.15)';
      ctx.fillStyle = 'rgba(30,60,90,0.06)';
      ctx.beginPath(); ctx.ellipse(CX * 0.5, CY * 0.5, 180, 110, 0.4, 0, Math.PI * 2); ctx.fill();
      ctx.restore();

      ctx.save();
      for (let i = 0; i < 250; i++) {
        const sx = (i * 137.508 + 33) % canvas.width;
        const sy = (i * 97.3 + 71) % canvas.height;
        const op = 0.2 + ((Math.sin(i * 0.7 + t * 0.3) + 1) / 2) * 0.5;
        ctx.fillStyle = `rgba(255,255,255,${op})`;
        ctx.beginPath(); ctx.arc(sx, sy, 0.5 + (i % 2) * 0.5, 0, Math.PI * 2); ctx.fill();
      }
      ctx.restore();

      for (let i = 0; i < 70; i++) {
        const frac = i / 70;
        const rx = 90 + frac * 130 + Math.sin(i * 0.9) * 3;
        const ry = rx * TILT + breathe * rx * 0.02;
        ringRots[i] += (0.0008 - frac * 0.0006) * speedMult;
        const rot = ringRots[i];
        const jx = Math.sin(i * 1.7 + t * 0.4) * 2;
        const jy = Math.cos(i * 2.3 + t * 0.3) * 1;
        let r, g, b, a;
        if (frac < 0.25) { const p = frac / 0.25; r = 255; g = Math.round(210 - p * 40); b = Math.round(100 - p * 50); a = (0.9 - p * 0.2) * diskOpacity; }
        else if (frac < 0.55) { const p = (frac - 0.25) / 0.3; r = Math.round(255 - p * 55); g = Math.round(170 - p * 40); b = Math.round(50 - p * 10); a = (0.7 - p * 0.2) * diskOpacity; }
        else if (frac < 0.8) { const p = (frac - 0.55) / 0.25; r = Math.round(200 - p * 80); g = Math.round(130 - p * 60); b = Math.round(40 - p * 10); a = (0.5 - p * 0.2) * diskOpacity; }
        else { const p = (frac - 0.8) / 0.2; r = Math.round(120 - p * 120); g = Math.round(70 - p * 70); b = Math.round(20 - p * 20); a = (0.15 - p * 0.15) * diskOpacity; }
        if (a <= 0) continue;
        ctx.save();
        ctx.translate(CX + jx, CY + jy); ctx.rotate(rot);
        ctx.strokeStyle = `rgba(${r},${g},${b},${a})`; ctx.lineWidth = Math.max(0.5, 1.5 - frac);
        ctx.beginPath(); ctx.ellipse(0, 0, rx, ry, 0, 0, Math.PI * 2); ctx.stroke();
        ctx.restore();
      }

      for (let i = 0; i < 18; i++) {
        const frac = i / 18, side = i % 2 === 0 ? 1 : -1;
        const arcY = CY - 68 * side;
        const osc = (Math.sin(t * 0.5 + i * 0.7) + 1) / 2;
        const a = (0.4 - frac * 0.25) * (0.6 + osc * 0.4) * diskOpacity;
        ctx.save();
        ctx.strokeStyle = `rgba(255,${Math.round(200 + frac * 30)},80,${a})`;
        ctx.lineWidth = 0.5 + (1 - frac) * 0.5;
        ctx.beginPath();
        ctx.moveTo(CX - (80 + frac * 40), arcY);
        ctx.bezierCurveTo(CX - 140 - frac * 20, CY - 120 * side, CX + 140 + frac * 20, CY - 120 * side, CX + (80 + frac * 40), arcY);
        ctx.stroke();
        ctx.restore();
      }

      ctx.save();
      const grd = ctx.createRadialGradient(CX, CY, 60, CX, CY, 100);
      grd.addColorStop(0, 'rgba(255,180,60,0.15)'); grd.addColorStop(1, 'rgba(255,180,60,0)');
      ctx.fillStyle = grd; ctx.beginPath(); ctx.arc(CX, CY, 100, 0, Math.PI * 2); ctx.fill();
      ctx.restore();

      ctx.save();
      ctx.fillStyle = '#000'; ctx.shadowBlur = 20; ctx.shadowColor = 'rgba(255,180,60,0.3)';
      ctx.beginPath(); ctx.arc(CX, CY, 70, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = 'rgba(255,190,50,0.6)'; ctx.lineWidth = 2; ctx.stroke();
      ctx.restore();

      const jetOp = state === 'processing' ? 0.9 : state === 'idle' ? 0.2 + Math.sin(t * 1.2) * 0.15 : 0.5 + Math.sin(t * 0.8) * 0.2;
      ctx.save();
      const tg = ctx.createLinearGradient(CX, CY - 70, CX, 0);
      tg.addColorStop(0, `rgba(255,220,100,${jetOp})`); tg.addColorStop(1, 'rgba(255,220,100,0)');
      ctx.strokeStyle = tg; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(CX, CY - 70); ctx.lineTo(CX, 0); ctx.stroke();
      const bg2 = ctx.createLinearGradient(CX, CY + 70, CX, canvas.height);
      bg2.addColorStop(0, `rgba(255,220,100,${jetOp})`); bg2.addColorStop(1, 'rgba(255,220,100,0)');
      ctx.strokeStyle = bg2;
      ctx.beginPath(); ctx.moveTo(CX, CY + 70); ctx.lineTo(CX, canvas.height); ctx.stroke();
      ctx.restore();

      for (const p of particles) {
        p.angle += p.angularVelocity * pSpeed;
        const px = CX + Math.cos(p.angle) * p.radius;
        const py = CY + Math.sin(p.angle) * p.radius * TILT;
        if (p.hasTrail) {
          p.trail.push({ x: px, y: py, op: p.opacity });
          if (p.trail.length > 5) p.trail.shift();
          for (let ti = 0; ti < p.trail.length; ti++) {
            const tp = p.trail[ti];
            ctx.fillStyle = `rgba(${hexToRgb(p.color)},${tp.op * (ti / p.trail.length) * 0.4})`;
            ctx.beginPath(); ctx.arc(tp.x, tp.y, p.size * 0.6, 0, Math.PI * 2); ctx.fill();
          }
        }
        const df = (p.radius - 100) / 160;
        ctx.fillStyle = `rgba(${hexToRgb(p.color)},${p.opacity * (1 - df * 0.6)})`;
        ctx.beginPath(); ctx.arc(px, py, p.size, 0, Math.PI * 2); ctx.fill();
        if (state === 'processing' && Math.random() < 0.003) {
          const fa = Math.random() * Math.PI * 2, fl = 20 + Math.random() * 30;
          ctx.save(); ctx.strokeStyle = 'rgba(255,200,80,0.6)'; ctx.lineWidth = 0.5;
          ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(px + Math.cos(fa) * fl, py + Math.sin(fa) * fl); ctx.stroke(); ctx.restore();
        }
      }

      if (state === 'listening' && now - lastRipple > 800) { ripples.push({ r: 70, startTime: now }); lastRipple = now; }
      if (state === 'responding' && ripples.length === 0) { ripples.push({ r: 70, startTime: now }); }
      ripples = ripples.filter(rp => {
        const el = (now - rp.startTime) / 1500;
        if (el >= 1) return false;
        ctx.save();
        ctx.strokeStyle = `rgba(255,200,80,${0.6 * (1 - el)})`;
        ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.arc(CX, CY, 70 + el * 130, 0, Math.PI * 2); ctx.stroke();
        ctx.restore();
        return true;
      });

      const nameY = CY - 88;
      const flicker = state === 'processing' ? (Math.random() > 0.08 ? 1 : 0.3) : 1;
      const nameOp = state === 'idle' ? 0.28 + Math.sin(t * 0.7) * 0.05
        : state === 'listening' ? 0.75 + Math.sin(t * 2.5) * 0.1
        : state === 'processing' ? 0.9 * flicker
        : 0.55 + Math.sin(t * 1.0) * 0.12;
      const nameRgb = STATE_CONFIG[state].nameRgb;

      ctx.save();
      ctx.shadowBlur = state === 'listening' ? 18 : state === 'processing' ? 28 : state === 'responding' ? 14 : 6;
      ctx.shadowColor = state === 'listening' ? 'rgba(255,210,100,0.9)'
        : state === 'processing' ? 'rgba(255,140,40,1)'
        : state === 'responding' ? 'rgba(255,190,80,0.7)'
        : 'rgba(255,200,80,0.3)';
      ctx.fillStyle = `rgba(${nameRgb},${nameOp})`;
      ctx.font = "500 11px 'Inter',sans-serif";
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      const letters = 'ALFRED', spacing = 7.5, totalW = (letters.length - 1) * spacing;
      for (let li = 0; li < letters.length; li++) {
        ctx.fillText(letters[li], CX - totalW / 2 + li * spacing, nameY);
      }
      ctx.strokeStyle = `rgba(${nameRgb},${nameOp * 0.5})`;
      ctx.lineWidth = 0.5;
      ctx.beginPath(); ctx.moveTo(CX - totalW / 2 - 4, nameY + 9); ctx.lineTo(CX + totalW / 2 + 4, nameY + 9); ctx.stroke();
      ctx.restore();

      ctx.restore();

      animRef.current = requestAnimationFrame(drawFrame);
    }

    animRef.current = requestAnimationFrame(drawFrame);
    return () => cancelAnimationFrame(animRef.current);
  }, []);

  return (
    <div id="canvas-wrap">
      <canvas id="bhCanvas" ref={canvasRef} width={600} height={600} />
      <div id="vignette" />
    </div>
  );
}