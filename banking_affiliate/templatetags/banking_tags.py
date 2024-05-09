from django.template import Library, Context, Template
# from sims.services.sim_service import getSims
from banking_affiliate.constants import telco_fee_ck

register = Library()

# @register.simple_tag(takes_context=True)
# def sim_block(context, title, query_str, link_more, store_type=None):
#     theme_folder = context["theme_folder"]
#     tenant = context["tenant"]
#     params = dict(parse_qsl(query_str))
#     params['store_type'] = store_type
#     response_data = getSims(params, tenant, None)
#     listSim = response_data['data'] if 'data' in response_data else []
#     t = loader.get_template(f'{theme_folder}/sims/sim-block.html')
#     return t.render({
#         'listSim': listSim,
#         'title': title,
#         'link_more': link_more,
#         'theme_folder': theme_folder
#     })
@register.filter
def get_ck_detail(sim):
    if sim['ck'] and sim['ct']:
        return "{:,.0f}₫ / {} tháng".format(sim['ck'], sim['ct'])
    return ""



@register.filter
def get_ck_promotion(sim):
    if int(sim['ck'])>0  and int(sim['t']) in telco_fee_ck:
        ck_telco = telco_fee_ck[sim['t']]
        if sim['ck'] in ck_telco:
            return "<br />".join(ck_telco[sim['ck']])
        else:
            for key, ck in ck_telco.items():
                if key == 0:
                    return "<br />".join(ck)
    return ""

