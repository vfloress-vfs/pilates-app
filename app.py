-- Protege el cambio de estado incluso si se actualiza sesiones_clase directamente.
-- Ejecutar una vez en Supabase > SQL Editor.
CREATE OR REPLACE FUNCTION public.validar_cierre_sesion_con_reserva()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    ahora_local timestamp without time zone := timezone('America/Lima', now());
BEGIN
    IF NEW.estado = 'Realizada' AND OLD.estado IS DISTINCT FROM 'Realizada' THEN
        IF (NEW.fecha_clase + NEW.hora_fin) > ahora_local THEN
            RAISE EXCEPTION 'No se puede marcar como realizada antes de la fecha y hora de fin de la clase.';
        END IF;
        IF NOT EXISTS (
            SELECT 1 FROM public.reservas r
            WHERE r.sesion_id = NEW.id
              AND r.alumno_id IS NOT NULL
              AND translate(lower(coalesce(r.estado, '')), 'áéíóúüñ', 'aeiouun') IN (
                  'asistencia', 'asistio', 'presente',
                  'inasistencia', 'no asistio', 'ausente', 'falta', 'no show', 'no-show'
              )
        ) THEN
            RAISE EXCEPTION 'No se puede cerrar una clase sin reservas con asistencia o inasistencia registrada.';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS sesiones_clase_validar_cierre ON public.sesiones_clase;
CREATE TRIGGER sesiones_clase_validar_cierre
    BEFORE UPDATE OF estado ON public.sesiones_clase
    FOR EACH ROW
    EXECUTE FUNCTION public.validar_cierre_sesion_con_reserva();

-- Marca inasistencias primero y cierra después solo clases con reservas de alumnos.
CREATE OR REPLACE FUNCTION public.marcar_inasistencias_vencidas()
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    ahora_local timestamp without time zone := timezone('America/Lima', now());
    inasistencias_marcadas integer;
BEGIN
    UPDATE public.reservas r
    SET estado = 'Inasistencia', fecha_inasistencia = now(), qr_token = NULL
    FROM public.sesiones_clase s
    WHERE r.sesion_id = s.id
      AND r.estado = 'Programada'
      AND s.estado = 'Programada'
      AND (s.fecha_clase + s.hora_fin) <= ahora_local;
    GET DIAGNOSTICS inasistencias_marcadas = ROW_COUNT;

    UPDATE public.sesiones_clase s
    SET estado = 'Realizada'
    WHERE s.estado = 'Programada'
      AND (s.fecha_clase + s.hora_fin) <= ahora_local
      AND EXISTS (
          SELECT 1 FROM public.reservas r
          WHERE r.sesion_id = s.id
            AND r.alumno_id IS NOT NULL
            AND translate(lower(coalesce(r.estado, '')), 'áéíóúüñ', 'aeiouun') IN (
                'asistencia', 'asistio', 'presente',
                'inasistencia', 'no asistio', 'ausente', 'falta', 'no show', 'no-show'
            )
      );
    RETURN inasistencias_marcadas;
END;
$$;

GRANT EXECUTE ON FUNCTION public.marcar_inasistencias_vencidas() TO anon, authenticated;

-- Guarda quién solicitó un reintento manual y el resultado del procesamiento.
CREATE TABLE IF NOT EXISTS public.reintentos_cierre_clases (
    id bigserial PRIMARY KEY,
    realizado_en timestamptz NOT NULL DEFAULT now(),
    realizado_por integer REFERENCES public.usuarios_admin(id) ON DELETE SET NULL,
    inasistencias_marcadas integer NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS reintentos_cierre_clases_fecha_idx
    ON public.reintentos_cierre_clases (realizado_en DESC);

CREATE OR REPLACE FUNCTION public.reintentar_cierre_clases(p_admin_id integer)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    total_inasistencias integer;
BEGIN
    total_inasistencias := public.marcar_inasistencias_vencidas();
    INSERT INTO public.reintentos_cierre_clases (realizado_por, inasistencias_marcadas)
    VALUES (p_admin_id, total_inasistencias);
    RETURN total_inasistencias;
END;
$$;

GRANT EXECUTE ON FUNCTION public.reintentar_cierre_clases(integer) TO anon, authenticated;
