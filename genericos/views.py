from braces.views import JSONResponseMixin
from django.views import generic

from sistema.models import SolicitudCredito


class TableAsJSON(JSONResponseMixin, generic.View):
    model = SolicitudCredito

    def get(self, request, *args, **kwargs):
        col_name_map = {
            '0': 'socio',
            '1': 'fecha_ingreso',
            '2': 'monto',
            '3': 'clasecredito',
            '4': 'estado',
            '5': 'acciones',
        }
        object_list = self.model.objects.all()
        search_text = request.GET.get('sSearch', '').lower()
        start = int(request.GET.get('iDisplayStart', 0))
        delta = int(request.GET.get('iDisplayLength', 50))
        sort_dir = request.GET.get('sSortDir_0', 'asc')
        sort_col = int(request.GET.get('iSortCol_0', 0))
        sort_col_name = request.GET.get('mDataProp_%s' % sort_col, '1')
        sort_dir_prefix = (sort_dir == 'desc' and '-' or '')

        if sort_col_name in col_name_map:
            sort_col = col_name_map[sort_col_name]
            object_list = object_list.order_by('%s%s' % (sort_dir_prefix, sort_col))

        filtered_object_list = object_list
        if len(search_text) > 0:
            filtered_object_list = object_list.filter_on_search(search_text)

        json = {
            "iTotalRecords": object_list.count(),
            "iTotalDisplayRecords": filtered_object_list.count(),
            "sEcho": request.GET.get('sEcho', 1),
            "aaData": [obj.as_list('/' + self.kwargs['app'] + '/solicitudcreditoupdate/') for obj in
                       filtered_object_list[start:(start + delta)]]
        }
        return self.render_json_response(json)
