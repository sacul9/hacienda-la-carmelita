/**
 * Composable de Agentes IA — Sprint 8
 * Gestiona artículos de blog generados por SEO/GEO y la generación de nuevo contenido.
 */

// ── Tipos ─────────────────────────────────────────────────────────────────────

export interface ArticuloBlog {
  id: string
  slug: string
  titulo_es: string
  titulo_en: string | null
  contenido_es: string
  contenido_en: string | null
  resumen_es: string | null
  resumen_en: string | null
  palabras_clave: string[] | null
  meta_descripcion_es: string | null
  meta_descripcion_en: string | null
  schema_markup: Record<string, unknown> | null
  autor_agente: string | null
  publicado: boolean
  fecha_publicacion: string | null
  created_at: string
  updated_at: string
}

interface ArticulosResponse {
  articulos: ArticuloBlog[]
  total: number
  page: number
}

// ── Composable ────────────────────────────────────────────────────────────────

export const useAgentes = () => {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  const articulos = ref<ArticuloBlog[]>([])
  const articuloCargando = ref(false)
  const seoGenerando = ref(false)
  const geoGenerando = ref(false)

  const _authHeaders = computed(() => {
    const token = authStore.token
    return token ? { Authorization: `Bearer ${token}` } : {}
  })

  /**
   * Obtiene la lista de artículos publicados (pública).
   */
  const fetchArticulos = async (params: { page?: number; limit?: number; todos?: boolean } = {}) => {
    articuloCargando.value = true
    try {
      const query: Record<string, any> = {
        page: params.page ?? 1,
        limit: params.limit ?? 10,
      }
      if (params.todos) query.todos = true

      const data = await $fetch<ArticulosResponse>(
        `${config.public.apiBase}/agentes/seo/articulos`,
        { params: query }
      )
      articulos.value = data.articulos ?? []
    } catch (e: any) {
      console.error('[useAgentes] fetchArticulos error:', e?.data?.detail ?? e?.message)
      articulos.value = []
    } finally {
      articuloCargando.value = false
    }
  }

  /**
   * Obtiene un artículo individual por slug (público).
   * Retorna null si no se encuentra o hay error.
   */
  const fetchArticulo = async (slug: string): Promise<ArticuloBlog | null> => {
    articuloCargando.value = true
    try {
      return await $fetch<ArticuloBlog>(
        `${config.public.apiBase}/agentes/seo/articulos/${slug}`
      )
    } catch (e: any) {
      const status = e?.response?.status ?? e?.statusCode
      if (status !== 404) {
        console.error('[useAgentes] fetchArticulo error:', e?.data?.detail ?? e?.message)
      }
      return null
    } finally {
      articuloCargando.value = false
    }
  }

  /**
   * Solicita al agente SEO generar un nuevo artículo (requiere token admin).
   */
  const generarSEO = async (): Promise<{ message: string; task_id: string }> => {
    seoGenerando.value = true
    try {
      return await $fetch<{ message: string; task_id: string }>(
        `${config.public.apiBase}/agentes/seo/generar`,
        {
          method: 'POST',
          headers: _authHeaders.value,
        }
      )
    } catch (e: any) {
      console.error('[useAgentes] generarSEO error:', e?.data?.detail ?? e?.message)
      throw e
    } finally {
      seoGenerando.value = false
    }
  }

  /**
   * Solicita al agente GEO regenerar llms.txt (requiere token admin).
   */
  const generarGEO = async (): Promise<{ message: string; task_id: string }> => {
    geoGenerando.value = true
    try {
      return await $fetch<{ message: string; task_id: string }>(
        `${config.public.apiBase}/agentes/geo/generar`,
        {
          method: 'POST',
          headers: _authHeaders.value,
        }
      )
    } catch (e: any) {
      console.error('[useAgentes] generarGEO error:', e?.data?.detail ?? e?.message)
      throw e
    } finally {
      geoGenerando.value = false
    }
  }

  return {
    articulos,
    articuloCargando,
    seoGenerando,
    geoGenerando,
    fetchArticulos,
    fetchArticulo,
    generarSEO,
    generarGEO,
  }
}
