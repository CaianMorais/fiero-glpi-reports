from django.shortcuts import render
from django.core.paginator import Paginator
from django.db import connections
from .forms import FiltroConsulta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
import csv

@login_required
def home(request):
    return render(request, "reports/home.html", {})

def _fetch_all_dict(cursor):
    """Converte fetchall() para lista de dicts usando cursor.description."""
    cols = [col[0] for col in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]

@login_required
def chamados_por_area(request):
    form = FiltroConsulta(request.GET or None)
    rows = []
    page_obj = None
    total = 0

    if form.is_valid():
        inicio = form.cleaned_data['inicio']
        fim = form.cleaned_data['fim']
        status = form.cleaned_data['status']

        sql = """
        WITH RECURSIVE cat_up AS (
            SELECT
                c.id AS cat_id,
                c.itilcategories_id AS parent_id,
                c.level,
                c.completename,
                CASE WHEN c.level = 2 THEN c.id END AS l2_id,
                CASE WHEN c.level = 2 THEN c.completename END AS l2_name
            FROM glpi_itilcategories c

            UNION ALL

            SELECT
                cu.cat_id,
                p.itilcategories_id AS parent_id,
                p.level,
                p.completename,
                CASE WHEN p.level = 2 THEN p.id ELSE cu.l2_id END AS l2_id,
                CASE WHEN p.level = 2 THEN p.completename ELSE cu.l2_name END AS l2_name
            FROM glpi_itilcategories p
            JOIN cat_up cu ON p.id = cu.parent_id
            WHERE cu.l2_id IS NULL
            ),
            cat_map AS (
            SELECT cat_id, MAX(l2_id) AS l2_id, MAX(l2_name) AS l2_name
            FROM cat_up
            GROUP BY cat_id
            ),
            user_main_group AS (
            SELECT users_id, MIN(groups_id) AS groups_id
            FROM glpi_groups_users
            WHERE groups_id <> 23           -- ignora o grupo 23 aqui também
            GROUP BY users_id
            )

            SELECT
                g.name AS grupo_requisitante,
                COALESCE(cm.l2_name, 'Sem categoria (nível 2)') AS categoria_nivel2,
                COUNT(DISTINCT t.id) AS qtde_chamados
            FROM glpi_tickets t
            JOIN glpi_tickets_users tu ON tu.tickets_id = t.id AND tu.type = 1
            JOIN glpi_users u ON u.id = tu.users_id AND u.is_active = 1 AND u.is_deleted = 0
            JOIN user_main_group umg ON umg.users_id = u.id
            JOIN glpi_groups g ON g.id = umg.groups_id
            LEFT JOIN cat_map cm ON cm.cat_id = t.itilcategories_id
            WHERE t.is_deleted = 0
            AND t.date BETWEEN %s AND %s
            AND t.status IN (%s)
            GROUP BY g.id, categoria_nivel2
            ORDER BY g.name ASC, qtde_chamados DESC;
        """
        params = [inicio, fim, status]

        with connections['glpi'].cursor() as cur:
            cur.execute(sql, params)
            rows = _fetch_all_dict(cur)
            total = len(rows)

    paginator = Paginator(rows, 100)  # 50 por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "reports/chamados_por_area.html",
        {"form": form, "page_obj": page_obj, "total": total},
    )

@login_required
def chamados_por_area_csv(request):
    form = FiltroConsulta(request.GET or None)
    if not form.is_valid():
        return HttpResponseBadRequest("Inválidos.")
    
    inicio = form.cleaned_data['inicio']
    fim = form.cleaned_data['fim']
    status = form.cleaned_data['status']

    sql = """
    WITH RECURSIVE cat_up AS (
        SELECT
            c.id AS cat_id,
            c.itilcategories_id AS parent_id,
            c.level,
            c.completename,
            CASE WHEN c.level = 2 THEN c.id END AS l2_id,
            CASE WHEN c.level = 2 THEN c.completename END AS l2_name
        FROM glpi_itilcategories c

        UNION ALL

        SELECT
            cu.cat_id,
            p.itilcategories_id AS parent_id,
            p.level,
            p.completename,
            CASE WHEN p.level = 2 THEN p.id ELSE cu.l2_id END AS l2_id,
            CASE WHEN p.level = 2 THEN p.completename ELSE cu.l2_name END AS l2_name
        FROM glpi_itilcategories p
        JOIN cat_up cu ON p.id = cu.parent_id
        WHERE cu.l2_id IS NULL
        ),
        cat_map AS (
        SELECT cat_id, MAX(l2_id) AS l2_id, MAX(l2_name) AS l2_name
        FROM cat_up
        GROUP BY cat_id
        ),
        user_main_group AS (
        SELECT users_id, MIN(groups_id) AS groups_id
        FROM glpi_groups_users
        WHERE groups_id <> 23
        GROUP BY users_id
        )

        SELECT
            g.name AS grupo_requisitante,
            COALESCE(cm.l2_name, 'Sem categoria (nível 2)') AS categoria_nivel2,
            COUNT(DISTINCT t.id) AS qtde_chamados
        FROM glpi_tickets t
        JOIN glpi_tickets_users tu ON tu.tickets_id = t.id AND tu.type = 1
        JOIN glpi_users u ON u.id = tu.users_id AND u.is_active = 1 AND u.is_deleted = 0
        JOIN user_main_group umg ON umg.users_id = u.id
        JOIN glpi_groups g ON g.id = umg.groups_id
        LEFT JOIN cat_map cm ON cm.cat_id = t.itilcategories_id
        WHERE t.is_deleted = 0
        AND t.date BETWEEN %s AND %s
        AND t.status IN (%s)
        GROUP BY g.id, categoria_nivel2
        ORDER BY g.name ASC, qtde_chamados DESC;
    """
    params = [inicio, fim, status]

    with connections['glpi'].cursor() as cur:
        cur.execute(sql, params)
        rows = _fetch_all_dict(cur)

    filename = f"chamados_por_area_{inicio}_{fim}.csv"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    response.write('\ufeff')
    writer = csv.writer(response, delimiter=';', lineterminator='\n')
    writer.writerow(["Grupo requisitante", "Área do chamado", "Quantidade de chamados"])
    for r in rows:
        writer.writerow([
            r.get("grupo_requisitante", ""),
            r.get("categoria_nivel2", ""),
            r.get("qtde_chamados", 0),
        ])

    return response
# Create your views here.
