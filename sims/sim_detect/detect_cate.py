import re
from .constant import DEFAULT_NUMBER_PREFIX
from sims.common.choices import CATE_INSTALLMENT_ID

def get_cat_id(phone, price=0, is_installment = False):
    cat = []
    cat2 = None
    if price >= 50000000:
        cat.append(82)
        cat2 = 82
    pattern = r"(8683|1515|2626|2628|1368|1618|8683|5239|9279|3937|3938|3939|8386|8668|4648|4078|3468|1668|7939|7838|7878|2879|1102|6789|6758|3737|4404|49532626|5239|9279|3937|39|38|3939|3333|8386|8668|4648|4078|3468|6578|6868|1668|8686|73087|1122|6789|6758|0607|0378|8181|3737|6028|7762|3609|8163|9981|7749|6612|5510|1257|0908|8906|1110|7749|2204|4444|8648|0404|0805|3546|5505|2306|1314|5031|2412|1920227|151618|181818|191919|2204|1486|01234|456)$"
    if re.search(pattern, phone):
        cat.append(78)
        cat2 = cat2 if cat2 is not None else 78
    pattern = r"(000000000|111111111|222222222|333333333|444444444|555555555|666666666|777777777|888888888|999999999)$"
    if re.search(pattern, phone):
        pass
    else:
        pattern = r"(00000000|11111111|22222222|33333333|44444444|55555555|66666666|77777777|88888888|99999999)$" #Bát Quý
        if re.search(pattern, phone):
            pass
        else:
            if re.search(pattern, phone):
                cat.append(78)
                cat2 = cat2 if cat2 is not None else 78
            pattern = r"(0000000|1111111|2222222|3333333|4444444|5555555|6666666|7777777|8888888|9999999)$" #Thất quý
            if re.search(pattern, phone):
                pass
            else:
                pattern = r"(000000|111111|222222|333333|444444|555555|666666|777777|888888|999999)$" #Lục quý
                if re.search(pattern, phone):
                    cat.append(100)
                    cat2 = cat2 if cat2 is not None else 100
                else:
                    pattern = r"(00000|11111|22222|33333|44444|55555|66666|77777|88888|99999)$" #Ngũ quý
                    if re.search(pattern, phone):
                        cat.append(99)
                        cat2 = cat2 if cat2 is not None else 99
                    else:
                        pattern = r"(0000|1111|2222|3333|4444|5555|6666|7777|8888|9999)$" #Tứ quý
                        if re.search(pattern, phone):
                            cat.append(68)
                            cat2 = cat2 if cat2 is not None else 68
                        else:
                            pattern = r"(.*)(000000|111111|222222|333333|444444|555555|666666|777777|888888|999999)(.*)" #Lục quý giữa
                            if re.search(pattern, phone):
                                cat.append(105)
                                cat2 = cat2 if cat2 is not None else 105
                            else:
                                pattern = r"(.*)(00000|11111|22222|33333|44444|55555|66666|77777|88888|99999)(.*)" #Ngũ quý giữa
                                if re.search(pattern, phone):
                                    cat.append(104)
                                    cat2 = cat2 if cat2 is not None else 104
                                else:
                                    pattern = r"(.*)(0000|1111|2222|3333|4444|5555|6666|7777|8888|9999)(.*)" #Tứ quý giữa
                                    if re.search(pattern, phone):
                                        cat.append(103)
                                        cat2 = cat2 if cat2 is not None else 103
                                    else:
                                        pass
                                pattern = r"(000|111|222|333|444|555|666|777|888|999)$" #Tam hoa
                                if re.search(pattern, phone):
                                    cat.append(80)
                                    cat2 = cat2 if cat2 is not None else 80
                                    pattern = r"(000|111|222|333|444|555|666|777|888|999)$" #Tam hoa kép
                                    if re.search(pattern, phone[:-3]):
                                        cat.append(102)
                                        cat2 = 102
                                else:
                                    pattern = r"(((\d{3})\3)|((\d{2})\5\5)|((\d{4})\7)|(([0-9])\9\9\9([0-9])\10\10\10))$" #Taxi ABC.ABC, AB.AB.AB, ABCD.ABCD, AAAA.BBBB
                                    if re.search(pattern, phone):
                                        cat.append(74)
                                        cat2 = cat2 if cat2 is not None else 74
                                        sub_pattern = r'(\d{2})\1\1$' #Taxi AB.AB.AB
                                        if re.search(sub_pattern,phone):
                                            cat.append(127)
                                            cat2 = 127
                                        sub_pattern = r'(\d{3})\1$' #Taxi ABC.ABC
                                        if re.search(sub_pattern,phone):
                                            cat.append(126)
                                            cat2 = 126
                                        sub_pattern = r'(\d{4})\1$' #Taxi ABCD.ABCD
                                        if re.search(sub_pattern,phone):
                                            cat.append(128)
                                            cat2 = 128
                                    pattern = r"(66|88|68|86|88|69|96)$" #Lộc phát
                                    if re.search(pattern, phone):
                                        cat.append(73)
                                        cat2 = cat2 if cat2 is not None else 73
                                    pattern = r"(39|79)$" #Thần tài
                                    if re.search(pattern, phone):
                                        cat.append(72)
                                        cat2 = cat2 if cat2 is not None else 72
                                    pattern = r"(38|78)$" #Ông địa
                                    if re.search(pattern, phone):
                                        cat.append(70)
                                        cat2 = cat2 if cat2 is not None else 70
                                    pattern = r"((([0-9])([0-9])\4\3)|(([0-9])([0-9])([0-9])\8\7\6))$" #Gánh đảo AB.BA, ABC.CBA
                                    if re.search(pattern, phone):
                                        cat.append(79)
                                        cat2 = cat2 if cat2 is not None else 79
                                    pattern = r"(((\d{2})\3)|(([0-9])\5([0-9])\6))$" #Lặp kép AB.AB, AA.BB
                                    if re.search(pattern, phone):
                                        cat.append(67)
                                        cat2 = cat2 if cat2 is not None else 67
                                    arrc = list(phone)
                                    length = len(arrc) - 1
                                    if (arrc[length] == arrc[length - 1]) and (arrc[length - 2] == arrc[length - 3]): #kep
                                        cat.append(120)
                                        cat2 = cat2 if cat2 is not None else 120
                                        if (arrc[length - 4] == arrc[length - 5]) and (arrc[length - 2] == arrc[length - 3]):
                                            if (arrc[length - 4] == arrc[length - 5]) and (arrc[length - 6] == arrc[length - 7]): #kep 4
                                                cat.append(122)
                                                cat2 = 122
                                            else: #kep 3
                                                cat.append(121)
                                                cat2 = 121
                                    elif (arrc[length] == arrc[length - 2]) and (arrc[length - 1] == arrc[length - 3]): #lap
                                        cat.append(123)
                                        cat2 = cat2 if cat2 is not None else 123
                                        if (arrc[length - 4] == arrc[length - 2]) and (arrc[length - 5] == arrc[length - 3]):
                                            if (arrc[length - 4] == arrc[length - 6]) and (arrc[length - 5] == arrc[length - 7]): #lap 4
                                                cat.append(125)
                                                cat2 = 125
                                            else: #lap 3
                                                cat.append(124)
                                                cat2 = 124
    pattern = r"(789|678|567|456|345|234|123|012)$" #Tiến lên A(A+1)(A+2), AB.A(B+1).A(B+2), AB.(A+1)B.(A+2)B ??????????
    if re.search(pattern, phone):
        cat.append(81)
        cat2 = cat2 if cat2 is not None else 81
    pattern = r"((([0-9])\3[0-9]\3\3[0-9])|(([0-9])([0-9])\6\5([0-9])\7)|(([0-9])\9[0-9]([0-9])\10[0-9])|([0-9]([0-9])\12[0-9]\12\12))$" #Dễ nhớ AAB.AAC, ABB.ACC, AAB.CCD, ABB.CBB
    if re.search(pattern, phone):
        cat.append(76)
        cat2 = cat2 if cat2 is not None else 76
    pattern = r"(0[1-9]|[1-2][0-9]|31(?!(?:0[2469]|11))|30(?!02))(0[1-9]|1[0-2])(((19)?[5-9][0-9])|((20)?([0-1][0-9])|(2[0-4])))$" # năm sinh
    pattern_year = r"(19[5-9][0-9]|20([0-1][0-9])|202[0-4])$"
    if re.search(pattern, phone) or re.search(pattern_year, phone):
        cat.append(77)
        cat2 = cat2 if cat2 is not None else 77
    pattern = r"^(0913|0903|0983)" #Ðầu cổ 0913, 0903, 0983
    if re.search(pattern, phone):
        cat.append(106)
        cat2 = cat2 if cat2 is not None else 106
    cat.append(tinhnguhanh(phone))
    # sim đại cát, sim cát, sim bình, sim hung, sim đại hung
    remainder = int(phone[-4:])%80
    formatted_remainder = f"{remainder:02}" if remainder < 10 else str(remainder)
    if formatted_remainder in ["00","03","05","16","18","23","24","25","28","30","31","38","40","46","47","66","78","80"]:
        cat.append(115)
        cat2 = cat2 if cat2 is not None else 115
    if formatted_remainder in ["01","06","07","08","11","13","17","21","27","32","36","42","43","51","56","62","64","67","72","76"]:
        cat.append(116)
        cat2 = cat2 if cat2 is not None else 116
    if formatted_remainder in ["02","14","34","37","39","48","49","50","53","57","59","65","70","73","74","77"]:
        cat2 = cat2 if cat2 is not None else 117
        cat.append(117)
    if formatted_remainder in ["04","09","10","12","19","22","26","29","33","35","41","44","45","52","54","58","60","61","63","68","69","71","79"]:
        cat.append(118)
        cat2 = cat2 if cat2 is not None else 118
    if formatted_remainder in ["20","55","75"]:
        cat.append(119)
        cat2 = cat2 if cat2 is not None else 119
    # số máy bàn
    if phone[:4] in DEFAULT_NUMBER_PREFIX["DESKTOP_PHONE"]:
        cat.append(86)
        cat2 = cat2 if cat2 is not None else 86
    if len(cat) == 0:
        cat.append(84)
    # Sim trả góp
    if is_installment:
        cat.append(CATE_INSTALLMENT_ID)
    cat2 = cat2 if cat2 is not None else 84
    return [cat, cat2]

def tinhnguhanh(sosim):
    arrsim = list(sosim)
    arr = {x: arrsim.count(x) for x in arrsim}
    maxValue = max(arr.values())
    hanh = 0
    maxIndex = max(arr, key=arr.get)
    if maxValue >= 6:
        hanh = int(maxIndex)
    else:
        hanh = int(sosim[-1])
    res = ""
    if hanh == 6:
        return 110
    elif hanh == 7:
        return 110
    elif hanh == 3:
        return 111
    elif hanh == 4:
        return 111
    elif hanh == 1:
        return 112
    elif hanh == 9:
        return 113
    elif hanh == 0:
        return 114
    elif hanh == 2:
        return 114
    elif hanh == 5:
        return 114
    elif hanh == 8:
        return 114
    return res

