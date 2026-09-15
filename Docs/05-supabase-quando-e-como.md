# 05 — Supabase: quando entra e como

**Data:** 14/09/2026
**Resposta curta:** não agora. Na Fase 6, e por um motivo específico.

---

## 1. O protótipo não precisa de banco para funcionar

A experiência inteira — escolher faixa, ouvir trechos, desenhar, ajustar, assistir —
roda no navegador com `localStorage`. Nenhuma etapa do MVP depende de servidor.

O que o Supabase resolveria é outra coisa: **salvar e compartilhar composições**. Cada
pessoa termina a sua, recebe um link, e esse link abre a composição dela para qualquer
um. Num contexto acadêmico isso é bom de verdade — a turma faz, cada um manda o link, e
a banca abre sem instalar nada.

Mas isso é uma funcionalidade adicional, não a fundação.

## 2. Por que não começar por ele

Adicionar Supabase agora custa: variáveis de ambiente, cliente, políticas de RLS,
tratamento de erro de rede, estados de carregando e de falha — tudo isso **no momento em
que a atenção deveria estar em `AudioBufferSourceNode` e em curvas de banda**. É a fase
de maior risco do projeto; qualquer coisa que dispute foco ali sai caro.

E não há pressa técnica, porque o terreno já está preparado: `Composicao` foi modelada
como JSON puro serializável desde o início (PRD, seção 4). Guardar em `localStorage`
hoje e no Postgres depois é **a mesma estrutura de dados** — a troca é de destino, não
de formato.

Estimativa quando chegar a hora: uma tabela, duas políticas, duas funções. Uma tarde.

## 3. Vercel, sim, desde o primeiro commit

Diferente do banco. Deployar cedo é grátis e descobre problema de build antes que ele
vire surpresa.

**Limites do plano Hobby** que interessam aqui: 100 MB de upload por deployment e 100 GB
de transferência por mês. Nossos três áudios somam ~4,8 MB, e os mapas ~200 KB. Folga
enorme.

O plano Hobby é para uso não comercial — um protótipo acadêmico se encaixa.

**Se um dia os áudios crescerem muito** (faixas longas em alta qualidade), a saída é
mover só os arquivos de mídia para o **Supabase Storage** e manter o resto na Vercel.
Não é o caso agora.

---

## 4. O schema, para quando chegar a Fase 6

Uma tabela. Sem autenticação — o protótipo não tem login e não vai ter.

```sql
create table public.composicoes (
  id          uuid primary key default gen_random_uuid(),
  slug        text unique not null default encode(gen_random_bytes(6), 'hex'),
  faixa_id    text not null,
  titulo      text,
  autor_nome  text,
  elementos   jsonb not null,
  criado_em   timestamptz not null default now()
);

create index on public.composicoes (slug);
create index on public.composicoes (criado_em desc);

alter table public.composicoes enable row level security;

-- qualquer um lê (é o que faz o link funcionar)
create policy "leitura publica"
  on public.composicoes for select
  to anon using (true);

-- qualquer um cria, ninguém altera nem apaga
create policy "criacao publica"
  on public.composicoes for insert
  to anon with check (
    jsonb_array_length(elementos) between 1 and 120
    and length(coalesce(titulo, '')) <= 80
    and length(coalesce(autor_nome, '')) <= 60
  );
```

**Sobre não ter UPDATE nem DELETE:** é deliberado. Sem login não há como provar que quem
edita é quem criou. Uma composição salva é **imutável** — revisar significa salvar uma
nova, com slug novo. Isso é mais simples e mais honesto que fingir uma noção de dono que
não existe.

O `with check` da política de insert é a única defesa contra alguém despejar lixo na
tabela. Para um protótipo acadêmico que não vai ser divulgado, basta. Se algum dia
precisar de mais, o caminho é uma Edge Function com limite por IP — não vale antecipar.

### O que fica na aplicação

```ts
// salvar → devolve o slug para montar o link
async function salvar(c: Composicao): Promise<string>

// abrir /c/[slug] → carrega a composição em modo somente leitura,
// direto no Modo Cinema
async function carregar(slug: string): Promise<Composicao | null>
```

Duas rotas novas: `/c/[slug]` (assistir) e um botão "Salvar e compartilhar" no card de
fim do Modo Cinema.

### Atenção ao plano Free do Supabase

Projetos sem atividade são **pausados por inatividade** no plano gratuito. Para um
protótipo que pode ficar meses parado entre a entrega e a defesa, isso importa: vale
conferir a política vigente antes da apresentação e, se necessário, abrir o projeto uns
dias antes para garantir que está de pé. Confirme os limites atuais em
[supabase.com/pricing](https://supabase.com/pricing) — eles mudam.

**Plano B se isso incomodar:** a composição inteira cabe numa URL. Elementos são poucos
(máximo 120) e leves; comprimidos e codificados em base64 na query string, o link fica
grande mas funciona, **sem servidor nenhum**. Para um protótipo acadêmico, é uma
alternativa legítima ao banco — e imune a pausa por inatividade.

---

## 5. Resumo da decisão

| Quando | O quê |
|---|---|
| **Fase 1, hoje** | Vercel. Deploy no primeiro commit |
| **Fases 1 a 5** | `localStorage`. A `Composicao` já é JSON serializável |
| **Fase 6** | Supabase: uma tabela, duas políticas, duas rotas |
| **Se der problema** | Composição na URL comprimida, sem servidor |

---

**Fontes:** [Vercel — Limits](https://vercel.com/docs/limits) · [Supabase — Pricing](https://supabase.com/pricing)
