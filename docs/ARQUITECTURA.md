# Arquitectura Técnica — Hacienda La Carmelita

## Diagrama de componentes

```
[Usuario / Huésped]
        │
        ▼
[Cloudflare CDN/WAF]
        │
   ┌────┴────┐
   │         │
[Vercel]  [Vercel]
[Nuxt SSR] [PWA]
   │
   │ API calls
   ▼
[Railway]
[FastAPI + Uvicorn]
   │         │
   ├─[Supabase PostgreSQL]
   ├─[Upstash Redis]
   ├─[Celery Workers]
   │     ├─[seo_agent]
   │     ├─[geo_agent]
   │     └─[sync_agent → Lodgify → Airbnb/Booking]
   │
   ├─[Twilio SMS/WhatsApp]
   ├─[SendGrid Email]
   ├─[Wompi Pagos CO]
   ├─[Stripe Pagos INT]
   └─[Anthropic Claude API]
```

## Flujo de reserva (happy path)

```
1. Usuario visita haciendalacarmelita.com
2. Selecciona fechas disponibles (GET /disponibilidad)
3. Elige SKU y add-ons (precio calculado en tiempo real)
4. Llena datos personales
5. Selecciona canal OTP → recibe código en 10s
6. Ingresa código de 6 dígitos → verificado en <1s
7. Pago: Wompi (CO) o Stripe (INT)
8. Webhook de pago confirmado → reserva CONFIRMADA
9. Email + WhatsApp enviados automáticamente
10. Disponibilidad bloqueada en Airbnb + Booking vía Lodgify
```

## Decisiones de arquitectura

| Decisión | Alternativa descartada | Razón |
|----------|----------------------|-------|
| SSE para chat (no WebSocket) | WebSocket | Más estable en Vercel/Railway serverless |
| SHA-256 para OTP | bcrypt | OTP de corta vida (<10min), SHA-256 suficiente y más rápido |
| Lodgify como channel manager | Guesty | Más económico para MVP; migrar a Guesty si escala |
| FastAPI BackgroundTasks para MVP | Celery desde día 1 | Menor complejidad; Celery se activa en Sprint 7+ |
| Supabase para auth | Auth propio | Ahorra 2 semanas de desarrollo de auth seguro |
