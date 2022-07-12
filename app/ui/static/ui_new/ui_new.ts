/// <reference path ="../node_modules/@types/jquery/dist/jquery.slim.d.ts"/> 
/// <reference path ="../node_modules/@types/select2/index.d.ts"/> 
import { isFunctionDeclaration } from "typescript";

// defining variables
const custom_colors: { [index: string]: any } = {
    "color1": "teal", // indigo
    "color2": "light",
    "color3": "red",
    "color4": "green",
    "color5": "grey",
    "color6": "dark",
    "color7": "blue",
    "color8": "white",
    "color9": "yellow",
    "color10": "orange"
}
// 

// set custom colors
function AddCustomColorClass() {

    // let custom_colors: {[index: string]: any} = {
    //     "color1" : "indigo",
    //     "color2" : "light"
    // }

    $.each(custom_colors, function (key: string, value: string) {

        // colors
        $(".custom-color-" + key).addClass(value);
        $(".custom-color-outline-" + key).addClass(value);

        // buttons
        $(".custom-button-" + key).addClass('btn-' + value);
        $(".custom-button-outline-" + key).addClass('btn-outline-' + value);

        // bg
        $(".custom-bg-" + key).addClass('bg-' + value);

        // text
        $(".custom-text-" + key).addClass(value + '-text');

        // // border
        // $(".custom-border-" + key).addClass('border border-' + value);


    });

}

// fadeout messages
// function FadeoutMessages(){
//     $(".imessage").delay(4000).fadeOut("slow");
//     return;
// }

// highlight navbar
function SwitchCurrentActive() {
    $("li.nav-item").removeClass("active");
    if (window.location.pathname.indexOf("/admin") >= 0) {
        $("a.nav-link[href='" + '/admin/projects' + "'").parent().addClass("active");
    } else if(window.location.pathname.indexOf("/library") >= 0) {
        $("a.nav-link[href='" + '/library/projects' + "'").parent().addClass("active");
    } else {
        $("a.nav-link[href='" + window.location.pathname + "'").parent().addClass("active");
    }
}

// highlight project nav
function HighlightProjectActive(project_pk: number) {
    $("#project_link").find("[data-project_pk=" + project_pk + "]").addClass("active").removeClass("btn-light");
}

// prevent enter key
function PreventEnterKeyFn() {
    $(window).on("keydown", function (event) {

        let code: any;
        if (event.key !== undefined) {
            code = event.key;
            // } else if (event.keyIdentifier !== undefined) {
            //     code = event.keyIdentifier;
        } else if (event.keyCode !== undefined) {
            code = event.keyCode;
        }

        if (code == 13) {
            event.preventDefault();
            return false;
        }
    });
}


// on next button
function GeneSpecificationSetStorage(project_pk: string, gene_specs_alt: any, mutation_status_tab?: string, mutation_status_tab_new?: boolean, next_btn?: boolean) {
    let itemkey: string = "gene_specs";
    let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
    // let custom_submit_button_disable_var: boolean = true;

    // var gene_specs_alt: any = window['gene_specs_alt'];

    if (Object.keys(myjson).length === 0) {
        GeneSpecificationGetStorage(project_pk);
        return;
    }

    // project_pk
    if (myjson.project_pk !== project_pk) {
        GeneSpecificationGetStorage(project_pk);
        return;
    }

    // get current tab
    if (!mutation_status_tab) {
        mutation_status_tab = $(".custom-tabs-mutation-status-tabs-div.show.active").attr("data-name");
    }

    // set mutation_status_list
    if (mutation_status_tab) {
        if (mutation_status_tab_new) {
            // check existing results
            if (myjson.mutation_status_list.indexOf(mutation_status_tab) > -1) {
                alert("This result already exist");
                return;
            } else {
                myjson.mutation_status_list.push(mutation_status_tab);
            }
            // check existing mutation status from db
            for (let k = 0; k < gene_specs_alt.length; k++) {
                if (myjson.id_method == gene_specs_alt[k].method_id && myjson.id_gene == gene_specs_alt[k].gene_id && mutation_status_tab == gene_specs_alt[k].status) {
                    alert("This result already exists for analysis method '" + gene_specs_alt[k].method__name + "' and gene '" + gene_specs_alt[k].gene__name + "'");
                    return;
                }
            }

        }
        myjson.mutation_status_current = mutation_status_tab;
    }

    // id_method and id_gene
    let that_var = ["id_method", "id_gene"]
    for (let i = 0; i < that_var.length; i++) {
        let that: string = "#" + that_var[i];
        let that_val: any = $(that).val();
        let that_next = $(that).parents("li").next("li");
        if (that_val.length > 0) {
            myjson[that_var[i]] = that_val;
            $(that).attr("disabled", "true");

            $(that).parents("li").removeClass().addClass("completed");
            $(that_next).removeClass().addClass("active");
            $(that_next).children(".custom-stepper-div").show("slow");
        }
    }

    // mutation_status_list from html to json
    if (next_btn) {
        if (myjson.id_gene.length > 0 && myjson.mutation_status_list.length <= 0) {
            localStorage.setItem(itemkey, JSON.stringify(myjson));
            alert("Please add at least one result");
            return;
        }
    }


    for (let i = 0; i < myjson.mutation_status_list.length; i++) {
        let mutation_status_name: string = myjson.mutation_status_list[i];
        if (mutation_status_tab) {
            if (mutation_status_tab !== mutation_status_name) {
                continue;
            }
        }
        if (myjson.mutation_status_dict[mutation_status_name] === undefined) {
            myjson.mutation_status_dict[mutation_status_name] = { "dpts": [], "dpts_shown": [] }
            // custom_submit_button_disable_var = false;
        } else {

            // if (myjson.mutation_status_dict[mutation_status_name].dpts.length <= 0) {
                // alert("Please add at least one datapoint type");
                // return;
                // if ($("#custom_submit_btn").attr("data-checkvar") != "true") {
                //     if (confirm('One of the results have no datapoints added. Are you sure to proceed?')) {
                //         // pass
                //         $("#custom_submit_btn").attr("data-checkvar", "true");
                //     } else {
                //         $("#custom_submit_btn").attr("data-checkvar", "false");
                //         return;
                //     }
                // }
            // }

            for (let j = 0; j < myjson.mutation_status_dict[mutation_status_name].dpts.length; j++) {
                let dpt_pk = myjson.mutation_status_dict[mutation_status_name].dpts[j], mutation_status_dpt_name: string = mutation_status_name + "_" + dpt_pk;

                // check shown
                if (myjson.mutation_status_dict[mutation_status_name].dpts_shown.indexOf(dpt_pk) > -1) {
                    // continue;
                } else {
                    myjson.mutation_status_dict[mutation_status_name].dpts_shown.push(dpt_pk);
                }

                myjson.mutation_status_dict[mutation_status_name][dpt_pk] = {
                    "pk": dpt_pk,
                    "mandatory": $("#" + mutation_status_dpt_name + "_mandatory").prop("checked"),
                    "default": $("#" + mutation_status_dpt_name + "_default").val()
                }

                // disable inputs
                // $("#" + mutation_status_dpt_name + "_tr").find("input").attr("disabled", true);
            }

            // submit button var
            // if ($("#custom_submit_btn").attr("data-checkvar") == "true") {
            //     custom_submit_button_disable_var = false;
            // } else {
            //     if (myjson.mutation_status_dict[mutation_status_name].dpts.length > 0) {
            //         custom_submit_button_disable_var = false;
            //     } else {
            //         custom_submit_button_disable_var = true;
            //     }
            // }
            
            // if (myjson.mutation_status_dict[mutation_status_name].dpts.length > 0) {
            //     custom_submit_button_disable_var = false;
            // } else {
            //     custom_submit_button_disable_var = true;
            // }



        }
    }

    if (mutation_status_tab_new) {
        // only when new tab is created
        MutationStatusTabs(myjson, itemkey);
    }
    localStorage.setItem(itemkey, JSON.stringify(myjson));

    // submit button
    // $("#custom_submit_btn").prop("disabled", custom_submit_button_disable_var);

    // submit button
    if(myjson.mutation_status_list.length <= 0) {
        $("#custom_submit_btn").prop("disabled", true);
    } else {
        $("#custom_submit_btn").prop("disabled", false);
    }
}

// on refresh
function GeneSpecificationGetStorage(project_pk: string) {
    let itemkey: string = "gene_specs";
    let myjsondef: { [index: string]: any } = {
        "project_pk": project_pk,
        "id_method": "",
        "id_gene": [],
        "mutation_status_list": [],
        "mutation_status_dict": {},
        "mutation_status_current": ""
    }

    let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
    if (Object.keys(myjson).length === 0) {
        localStorage.setItem(itemkey, JSON.stringify(myjsondef));
        return;
    }

    // project_pk
    if (myjson.project_pk !== project_pk) {
        localStorage.setItem(itemkey, JSON.stringify(myjsondef));
        return;
    }

    // id_method and id_gene
    let that_var = ["id_method", "id_gene"]
    for (let i = 0; i < that_var.length; i++) {

        let that: string = "#" + that_var[i];
        let that_next = $(that).parents("li").next("li");
        // if($(that).val() !== "" && $(that).val() !== []){
        if (myjson[that_var[i]] != "") {
            $(that).val(myjson[that_var[i]]);
            $(that).attr("disabled", "true");

            $(that).parents("li").removeClass().addClass("completed");
            $(that_next).removeClass().addClass("active");
            $(that_next).children(".custom-stepper-div").show("slow");

            $(that).trigger("change");

        }

    }

    // mutation_status_list from json to html
    MutationStatusTabs(myjson, itemkey);

    // submit button
    if(myjson.mutation_status_list.length <= 0) {
        $("#custom_submit_btn").prop("disabled", true);
    } else {
        $("#custom_submit_btn").prop("disabled", false);
    }

}


function MutationStatusTabs(myjson: any, itemkey: string) {
    let htmlstr: string = "";
    let htmldivstr: string = "";
    let mutation_status_tab_index: number = 0;

    if (myjson.mutation_status_current !== "") {
        mutation_status_tab_index = myjson.mutation_status_list.indexOf(myjson.mutation_status_current);
        if (mutation_status_tab_index == -1) {
            mutation_status_tab_index = 0;
        }
    }

    for (let i = 0; i < myjson.mutation_status_list.length; i++) {

        let mutation_status_name: string = myjson.mutation_status_list[i],
            active_var: string = "",
            show_var: string = "",
            aria_selected_var: string = "false";

        if (i === mutation_status_tab_index) {
            active_var = "active", show_var = "show", aria_selected_var = "true";
        }

        htmlstr += '<li class="nav-item custom-tabs-mutation-status-tabs-li" data-name="' + mutation_status_name + '">';
        htmlstr += '<a class="nav-link ' + active_var + '" id="' + mutation_status_name + '_tab" data-name="' + mutation_status_name + '" data-toggle="tab" href="#' + mutation_status_name + '_div" role="tab" aria-control="' + mutation_status_name + '_div" aria-selected="' + aria_selected_var + '"><h6><strong>' + mutation_status_name;
        htmlstr += '</strong></h6><i class="fas fa-times ml-auto text-danger custom-tabs-mutation-status-tab-delete" data-name="' + mutation_status_name + '" style="position: absolute; right: 5%; top: 5%"></i>';
        htmlstr += '</li></a>';

        htmldivstr += '<div class="tab-pane fade ' + show_var + ' ' + active_var + ' custom-tabs-mutation-status-tabs-div" id="' + mutation_status_name + '_div" data-name="' + mutation_status_name + '" role="tabpanel" aria-labelledby="' + mutation_status_name + '_div">';
        // htmldivstr += mutation_status_name;
        htmldivstr += '<table class="table table-sm overflow-auto" style="max-height:250px;"><thead><tr><th scope="col"><h6><strong>Datapoint Type</strong></h6></th><th scope="col"><h6><strong>Mandatory</strong></h6></th><th scope="col"><h6><strong>Default</strong></h6></th><th scope="col"></th></tr></thead><tbody>';

        htmldivstr += '</tbody></table>';
        htmldivstr += '</div>';

    }

    // set function
    htmldivstr += '<script>CustomSetAction1("' + itemkey + '");CustomMutationStatusRemoveBtn("' + itemkey + '");</script>';

    // remove previous data
    $(".custom-tabs-mutation-status-tabs-li").remove();
    $(htmlstr).insertBefore("#custom_mutation_status_tabs_add_li");
    $("#custom_mutation_status_contents").html(htmldivstr);

    MutationStatusTabsContents(myjson, itemkey);

    return;

}

function MutationStatusTabsContents(myjson: any, itemkey: string, check_shown?: boolean) {


    for (let i = 0; i < myjson.mutation_status_list.length; i++) {
        let mutation_status_name: string = myjson.mutation_status_list[i];

        if (myjson.mutation_status_dict[mutation_status_name] !== undefined) {
            for (let j = 0; j < myjson.mutation_status_dict[mutation_status_name].dpts.length; j++) {

                let dpt_pk: number = myjson.mutation_status_dict[mutation_status_name].dpts[j];

                if (check_shown) {
                    // check shown
                    if (myjson.mutation_status_dict[mutation_status_name].dpts_shown.indexOf(dpt_pk) > -1) {
                        continue;
                    } else {
                        myjson.mutation_status_dict[mutation_status_name].dpts_shown.push(dpt_pk);
                    }
                }

                let mutation_status_dpt_name: string = mutation_status_name + "_" + dpt_pk;
                // let clonediv = $('<div/>').append($('#custom_datapointtypes_li').find('span[data-dpt_pk=' + dpt_pk + ']').clone());
                // let reqspan = $('#custom_datapointtypes_li').find('span[data-dpt_pk=' + dpt_pk + ']');
                let reqspan = $('#custom_datapointtype_span').find('span[data-dpt_pk=' + dpt_pk + ']');
                let reqspan_helptext = reqspan.attr("title");
                let reqspan_options = reqspan.attr("data-options");

                let htmldivstr: string = '';
                htmldivstr += '<tr id="' + mutation_status_dpt_name + '_tr">';
                htmldivstr += '<td><h6><strong>' + reqspan.html() + '</strong></h6><input type="hidden" id="' + mutation_status_dpt_name + '_pk" value="' + dpt_pk + '"></td>';
                htmldivstr += '<td><div class="custom-control custom-checkbox"><input type="checkbox" class="custom-control-input" id="' + mutation_status_dpt_name + '_mandatory"><label class="custom-control-label" for="' + mutation_status_dpt_name + '_mandatory"></label></div></td>';
                htmldivstr += '<td class="md-form"><input type="text" id="' + mutation_status_dpt_name + '_default" class="form-control" value="">';
                if (reqspan_options !== "") {
                    htmldivstr += '<small>options: ' + reqspan_options + '</small>';
                }
                if (reqspan_helptext !== "") {
                    if (reqspan_options !== "") {
                        htmldivstr += '<br/>';
                    }
                    htmldivstr += '<small>helptext: ' + reqspan_helptext + '</small>';
                }
                htmldivstr += '</td>';
                htmldivstr += '<td><a class="text-danger custom-datapointtypes-li-delete-btn" data-name="' + mutation_status_name + '" data-dpt_pk="' + dpt_pk + '"><i class="fas fa-times"></i></a></td>';
                htmldivstr += '</tr>';

                // push
                $("#" + mutation_status_name + "_div").find("tbody").append(htmldivstr);

                // change mandatory and default values
                $("#" + mutation_status_dpt_name + "_mandatory").prop("checked", myjson.mutation_status_dict[mutation_status_name][dpt_pk].mandatory);

                $("#" + mutation_status_dpt_name + "_default").val(myjson.mutation_status_dict[mutation_status_name][dpt_pk].default);

            }
        }

    }
    $("#custom_mutation_status_contents_span").html('<script>CustomDptRemoveBtn("' + itemkey + '");</script>');
    return;

}

function CustomSetAction1(itemkey: string) {
    $(".custom-tabs-mutation-status-tabs-li").on("click", function () {
        // let itemkey: string = "gene_specs";
        let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
        myjson.mutation_status_current = $(this).children("a.nav-link").attr("data-name");
        localStorage.setItem(itemkey, JSON.stringify(myjson));
    });
}

function CustomMutationStatusRemoveBtn(itemkey: string) {
    $(".custom-tabs-mutation-status-tab-delete").on("click", function () {
        // let itemkey: string = "gene_specs";
        let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");

        // remove from myjson
        let mutation_status_name: any = $(this).attr("data-name");
        let mutation_status_list_index = myjson.mutation_status_list.indexOf(mutation_status_name);
        if (mutation_status_list_index > -1) {
            // myjson.mutation_status_list.pop(mutation_status_name);
            myjson.mutation_status_list.splice(mutation_status_list_index, 1);
        }
        if (Object.keys(myjson.mutation_status_dict).indexOf(mutation_status_name) > -1) {
            delete (myjson.mutation_status_dict[mutation_status_name]);
        }

        $("#custom_mutation_status_tabs").find("li[data-name=" + mutation_status_name + "]").remove();
        $("#custom_mutation_status_contents").find(".custom-tabs-mutation-status-tabs-div[data-name=" + mutation_status_name + "]").remove();

        if (myjson.mutation_status_current === mutation_status_name) {
            if (myjson.mutation_status_list.length > 0) {
                myjson.mutation_status_current = myjson.mutation_status_list[0];
            } else {
                myjson.mutation_status_current = "";
            }
        }

        // submit button
        if(myjson.mutation_status_list.length <= 0) {
            $("#custom_submit_btn").prop("disabled", true);
        } else {
            $("#custom_submit_btn").prop("disabled", false);
        }

        // update myjson
        localStorage.setItem(itemkey, JSON.stringify(myjson));
        $(this).parents("tr").remove();
    });
}

function CustomDptRemoveBtn(itemkey: string) {
    $(".custom-datapointtypes-li-delete-btn").on("click", function () {
        // let itemkey: string = "gene_specs";
        let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");

        // remove from myjson
        let mutation_status_name: any = $(this).attr("data-name"), dpt_pk: any = $(this).attr("data-dpt_pk");
        let mutation_status_dpt_list_index = myjson.mutation_status_dict[mutation_status_name].dpts.indexOf(dpt_pk);
        if (mutation_status_dpt_list_index > -1) {
            // myjson.mutation_status_dict[mutation_status_name].dpts.pop(dpt_pk);
            myjson.mutation_status_dict[mutation_status_name].dpts.splice(mutation_status_dpt_list_index, 1);
        }
        let mutation_status_dpt_shown_list_index = myjson.mutation_status_dict[mutation_status_name].dpts_shown.indexOf(dpt_pk);
        if (mutation_status_dpt_shown_list_index > -1) {
            // myjson.mutation_status_dict[mutation_status_name].dpts_shown.pop(dpt_pk);
            myjson.mutation_status_dict[mutation_status_name].dpts_shown.splice(mutation_status_dpt_shown_list_index, 1);
        }

        delete (myjson.mutation_status_dict[mutation_status_name][dpt_pk]);

        // update myjson
        localStorage.setItem(itemkey, JSON.stringify(myjson));
        $(this).parents("tr").remove();
    });
}

function CustomDptAddBtn(itemkey: string) {

    $(".custom-dpt-add-btn").on("click", function () {
        // let itemkey: string = "gene_specs";
        let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
        let this_pk: any = $(this).attr("data-dpt_pk");

        if (myjson.mutation_status_current === "") {
            // alert("Please add a mutation status first");
            alert("Please add a result first");
            return;
        }

        if (myjson.mutation_status_dict[myjson.mutation_status_current].dpts.indexOf(this_pk) > -1) {
            alert("Datapoint type has already been added");
            return;
        }

        // add dpts
        myjson.mutation_status_dict[myjson.mutation_status_current].dpts.push(this_pk);

        // setting default values if new
        if (Object.keys(myjson.mutation_status_dict[myjson.mutation_status_current]).indexOf(this_pk) == -1) {
            myjson.mutation_status_dict[myjson.mutation_status_current][this_pk] = {
                "pk": this_pk,
                "mandatory": false,
                "default": ""
            }
        }
        // create html
        MutationStatusTabsContents(myjson, itemkey, true);
        
        // submit button
        if(myjson.mutation_status_list.length <= 0) {
            $("#custom_submit_btn").prop("disabled", true);
        } else {
            $("#custom_submit_btn").prop("disabled", false);
        }

        // set itemkey
        localStorage.setItem(itemkey, JSON.stringify(myjson));

    });

}

// // on next button
// function ChipsetSpecificationSetStorage0(project_pk: string, chipset_specs_alt: any, mutation_status_tab?: string, mutation_status_tab_new?: boolean, next_btn?: boolean) {
//     let itemkey: string = "chipset_specs";
//     let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
//     let custom_submit_button_disable_var: boolean = true;

//     // var chipset_specs_alt: any = window['chipset_specs_alt'];

//     if (Object.keys(myjson).length === 0) {
//         ChipsetSpecificationGetStorage0(project_pk);
//         return;
//     }

//     // project_pk
//     if (myjson.project_pk !== project_pk) {
//         ChipsetSpecificationGetStorage0(project_pk);
//         return;
//     }

//     // get current tab
//     if (!mutation_status_tab) {
//         mutation_status_tab = $(".custom-tabs-mutation-status-tabs-div.show.active").attr("data-name");
//     }

//     // set mutation_status_list
//     if (mutation_status_tab) {
//         if (mutation_status_tab_new) {
//             // check existing results
//             if (myjson.mutation_status_list.indexOf(mutation_status_tab) > -1) {
//                 alert("This result already exist");
//                 return;
//             } else {
//                 myjson.mutation_status_list.push(mutation_status_tab);
//             }
//             // check existing mutation status from db
//             for (let k = 0; k < chipset_specs_alt.length; k++) {
//                 if (myjson.id_method == chipset_specs_alt[k].method_id && myjson.id_chipset == chipset_specs_alt[k].gene_id && mutation_status_tab == chipset_specs_alt[k].status) {
//                     alert("This result already exists for analysis method '" + chipset_specs_alt[k].method__name + "' and chipset '" + chipset_specs_alt[k].chipset__name + "'");
//                     return;
//                 }
//             }

//         }
//         myjson.mutation_status_current = mutation_status_tab;
//     }

//     // id_method and id_chipset
//     let that_var = ["id_method", "id_chipset"]
//     for (let i = 0; i < that_var.length; i++) {
//         let that: string = "#" + that_var[i];
//         let that_val: any = $(that).val();
//         let that_next = $(that).parents("li").next("li");
//         if (that_val.length > 0) {
//             myjson[that_var[i]] = that_val;
//             $(that).attr("disabled", "true");

//             $(that).parents("li").removeClass().addClass("completed");
//             $(that_next).removeClass().addClass("active");
//             $(that_next).children(".custom-stepper-div").show("slow");
//         }
//     }

//     // mutation_status_list from html to json
//     if (next_btn) {
//         if (myjson.id_chipset.length > 0 && myjson.mutation_status_list.length <= 0) {
//             localStorage.setItem(itemkey, JSON.stringify(myjson));
//             alert("Please add at least one result");
//             return;
//         }
//     }
//     for (let i = 0; i < myjson.mutation_status_list.length; i++) {
//         let mutation_status_name: string = myjson.mutation_status_list[i];
//         if (mutation_status_tab) {
//             if (mutation_status_tab !== mutation_status_name) {
//                 continue;
//             }
//         }
//         if (myjson.mutation_status_dict[mutation_status_name] === undefined) {
//             myjson.mutation_status_dict[mutation_status_name] = { "dpts": [], "dpts_shown": [] }
//             custom_submit_button_disable_var = true;
//         } else {

//             if (myjson.mutation_status_dict[mutation_status_name].dpts.length <= 0) {
//                 // alert("Please add at least one datapoint type");
//                 // return;
//                 if ($("#custom_submit_btn").attr("data-checkvar") != "true") {
//                     if (confirm('One of the results have no datapoints added. Are you sure to proceed?')) {
//                         // pass
//                         $("#custom_submit_btn").attr("data-checkvar", "true");
//                     } else {
//                         $("#custom_submit_btn").attr("data-checkvar", "false");
//                         return;
//                     }
//                 }
//             }

//             for (let j = 0; j < myjson.mutation_status_dict[mutation_status_name].dpts.length; j++) {
//                 let dpt_pk = myjson.mutation_status_dict[mutation_status_name].dpts[j], mutation_status_dpt_name: string = mutation_status_name + "_" + dpt_pk;

//                 // check shown
//                 if (myjson.mutation_status_dict[mutation_status_name].dpts_shown.indexOf(dpt_pk) > -1) {
//                     // continue;
//                 } else {
//                     myjson.mutation_status_dict[mutation_status_name].dpts_shown.push(dpt_pk);
//                 }

//                 myjson.mutation_status_dict[mutation_status_name][dpt_pk] = {
//                     "pk": dpt_pk,
//                     "mandatory": $("#" + mutation_status_dpt_name + "_mandatory").prop("checked"),
//                     "default": $("#" + mutation_status_dpt_name + "_default").val()
//                 }

//                 // disable inputs
//                 // $("#" + mutation_status_dpt_name + "_tr").find("input").attr("disabled", true);
//             }

//             // submit button var
//             if ($("#custom_submit_btn").attr("data-checkvar") == "true") {
//                 custom_submit_button_disable_var = false;
//             } else {
//                 if (myjson.mutation_status_dict[mutation_status_name].dpts.length > 0) {
//                     custom_submit_button_disable_var = false;
//                 } else {
//                     custom_submit_button_disable_var = true;
//                 }
//             }

//         }
//     }

//     if (mutation_status_tab_new) {
//         // only when new tab is created
//         MutationStatusTabs(myjson, itemkey);
//     }
//     localStorage.setItem(itemkey, JSON.stringify(myjson));

//     // submit button
//     $("#custom_submit_btn").prop("disabled", custom_submit_button_disable_var);
// }

// // on refresh
// function ChipsetSpecificationGetStorage0(project_pk: string) {
//     let itemkey: string = "chipset_specs";
//     let myjsondef: { [index: string]: any } = {
//         "project_pk": project_pk,
//         "id_method": "",
//         "id_chipset": [],
//         "mutation_status_list": [],
//         "mutation_status_dict": {},
//         "mutation_status_current": ""
//     }

//     let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
//     if (Object.keys(myjson).length === 0) {
//         localStorage.setItem(itemkey, JSON.stringify(myjsondef));
//         return;
//     }

//     // project_pk
//     if (myjson.project_pk !== project_pk) {
//         localStorage.setItem(itemkey, JSON.stringify(myjsondef));
//         return;
//     }

//     // id_method and id_chipset
//     let that_var = ["id_method", "id_chipset"]
//     for (let i = 0; i < that_var.length; i++) {

//         let that: string = "#" + that_var[i];
//         let that_next = $(that).parents("li").next("li");
//         // if($(that).val() !== "" && $(that).val() !== []){
//         if (myjson[that_var[i]] != "") {
//             $(that).val(myjson[that_var[i]]);
//             $(that).attr("disabled", "true");

//             $(that).parents("li").removeClass().addClass("completed");
//             $(that_next).removeClass().addClass("active");
//             $(that_next).children(".custom-stepper-div").show("slow");

//             $(that).trigger("change");

//         }

//     }

//     // mutation_status_list from json to html
//     MutationStatusTabs(myjson, itemkey);

// }


function GeneAnalysisSpecificationStepper(genespecs: any[]) {
    // gene_analysis_stepper.html

    // fade toggle
    $("#id_gene").parent("div").hide("slow");
    $("#id_status").parent("div").hide("slow");

    // add methods
    let methods: any[] = [];
    $.each(genespecs, function (i, val) {
        if (methods.length == 0) {
            methods.push('<option></option>');
        }
        let htmlstr: string = '<option value="' + val.method_id + '">' + val.method__name + '</option>';
        if (methods.indexOf(htmlstr) <= -1) {
            methods.push(htmlstr);
        }
    });
    $("#id_method").html(methods.join(''));

    $("#id_method").on("change", function () {
        // add genes
        let method_pk: any = $(this).val();
        let genes: any[] = [];
        $.each(genespecs, function (i, val) {
            if (genes.length == 0) {
                genes.push('<option></option>');
            }
            if (String(val.method_id) === String(method_pk)) {
                let htmlstr: string = '<option value="' + val.gene_id + '">' + val.gene__name + '</option>';
                if (genes.indexOf(htmlstr) <= -1) {
                    genes.push(htmlstr);
                }
            }
        });

        $("#id_status").val("").trigger("change");
        $("#id_gene").html(genes.join(''));
        $("#id_status").parent("div").hide("slow");
        $("#id_gene").parent("div").hide("slow");
        $("#id_gene").parent("div").show("slow");
        let that = $("#custom_stepper_horizontal_ul").find('li').first();
        $("#custom_stepper_horizontal_ul").find('li').removeClass();
        that.addClass("completed");
        that.next().addClass("active");
    });

    $("#id_gene").on("change", function () {
        // add genes
        let method_pk: any = $("#id_method").val();
        let gene_pk: any = $(this).val();
        let statuslist: any[] = [];
        $.each(genespecs, function (i, val) {
            if (statuslist.length == 0) {
                statuslist.push('<option></option>');
            }
            if (String(val.method_id) === String(method_pk) && String(val.gene_id) === String(gene_pk)) {
                let htmlstr: string = '<option value="' + val.pk + '">' + val.status + '</option>';
                if (statuslist.indexOf(htmlstr) <= -1) {
                    statuslist.push(htmlstr);
                }
            }
        });
        $("#id_status").val("").trigger("change");
        $("#id_status").html(statuslist.join(''));
        $("#id_status").parent("div").hide("slow");
        $("#id_status").parent("div").show("slow");
        let that = $("#custom_stepper_horizontal_ul").find('li.active');
        that.removeClass().addClass("completed");
        that.next().removeClass().addClass("active");
    });

    $("#id_status").on("change", function(){
        if($(this).val() == null || $(this).val() == "") {
            // $("#custom_stepper_submit_btn").prop("disabled", true);
        } else {
            let searchsubstr: string = window.location.search.substr(1);
            // $("#custom_stepper_submit_btn").prop("disabled", false);
            if (searchsubstr !== ""){
                window.location.href = window.location.pathname + "?genespec=" + $(this).val() + '&' + searchsubstr;
            } else {
                window.location.href = window.location.pathname + "?genespec=" + $(this).val();
            }
        }
    });

}

// chipset specification
function ChipsetSpecificationGetStorage(project_pk: string) {
    let itemkey: string = "chipset_specs";
    let myjsondef: { [index: string]: any } = {
        "project_pk": project_pk,
        "id_name_chipset": "",
        "id_manufacturer": "",
        "id_version": "",
        "id_genes": [],
        "dpts": [],
        "dpts_dict": {}
    }

    let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
    if (Object.keys(myjson).length === 0) {
        localStorage.setItem(itemkey, JSON.stringify(myjsondef));
        return;
    }

    // project_pk
    if (myjson.project_pk !== project_pk) {
        localStorage.setItem(itemkey, JSON.stringify(myjsondef));
        return;
    }

    let that_var: any[] = ["id_name_chipset", "id_manufacturer", "id_version", "id_genes"];
    let checkvar = true;
    for(let i=0; i<that_var.length; i++){
        let that: string = "#" + that_var[i];
        if (myjson[that_var[i]] != "") {
            $(that).val(myjson[that_var[i]]);
            $(that).trigger("change");
            $(that).prop("disabled", true);
        } else {
            checkvar = false;
        }
    }

    if(checkvar) {
        let that: any = $(".stepper.stepper-vertical").children("li").first();
        that.removeClass("active").addClass("completed");
        that.next().removeClass().addClass("active");
        that.next().children(".custom-stepper-div").show("slow");
    }

    // adding datapoints
    $.each(myjson.dpts, function(i, val){
        // add htmlstr to #custom_chipset_dpts_body
        let dpt_pk = val,
            name = myjson.dpts_dict[dpt_pk].name,
            dpt_name = 'dpt_' + dpt_pk,
            reqspan_helptext = myjson.dpts_dict[dpt_pk].helptext,
            reqspan_options = myjson.dpts_dict[dpt_pk].options,
            mandatory = myjson.dpts_dict[dpt_pk].mandatory,
            default_val = myjson.dpts_dict[dpt_pk].default;


        let htmlstr = '<tr data-pk="' + dpt_pk + '">'; 
            htmlstr += '<td><h6><strong>' + name + '</strong></h6><input type="hidden" id="' + dpt_name + '_pk" value="' + dpt_pk + '"></td>';
            htmlstr += '<td><div class="custom-control custom-checkbox"><input type="checkbox" class="custom-control-input" id="' + dpt_name + '_mandatory"><label class="custom-control-label" for="' + dpt_name + '_mandatory"></label></div></td>';
            htmlstr += '<td class="md-form"><input type="text" id="' + dpt_name + '_default" class="form-control" value="">';
            if( reqspan_options !== "" ) {
                htmlstr += '<small>options: ' + reqspan_options + '</small>';
            }
            if(reqspan_helptext !== "") {
                if( reqspan_options != "") {
                    htmlstr += '<br/>';
                }
                htmlstr += '<small>helptext: ' + reqspan_helptext + '</small>';
            }
            htmlstr += '</td>';
            htmlstr += '<td><a class="text-danger custom-datapointtypes-li-delete-btn" data-name="' + dpt_name + '" data-dpt_pk="' + dpt_pk + '" onclick="CustomChipsetDptsRemoveBtn(this);"><i class="fas fa-times"></i></a></td>';
            htmlstr += '</tr>';
            $("#custom_chipset_table_tbody").append(htmlstr);

            $("#" + dpt_name + '_mandatory').prop("checked", mandatory);
            $("#" + dpt_name + '_default').val(default_val);

    });

    if(myjson.dpts.length > 0) {
        $("#custom_submit_btn").prop("disabled", false);
    } else {
        $("#custom_submit_btn").prop("disabled", true);
    }

}
function ChipsetSpecificationSetStorage(project_pk: string) {
    let itemkey: string = "chipset_specs";
    let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");

    if (Object.keys(myjson).length === 0) {
        ChipsetSpecificationGetStorage(project_pk);
        return;
    }

    // project_pk
    if (myjson.project_pk !== project_pk) {
        ChipsetSpecificationGetStorage(project_pk);
        return;
    }

    let that_var: any[] = ["id_name_chipset", "id_manufacturer", "id_version", "id_genes"];
    let checkvar:boolean = true;
    for(let i=0; i<that_var.length; i++){
        let that: string = "#" + that_var[i];
        let that_val: any = $(that).val();
        if (that_val.length > 0) {
            myjson[that_var[i]] = that_val;
            $(that).prop("disabled", true);
        } else {
            $(that).prop("disabled", false);
            checkvar = false;
        }
    }

    if(checkvar) {
        let that: any = $(".stepper.stepper-vertical").children("li").first();
        that.removeClass("active").addClass("completed");
        that.next().removeClass().addClass("active");
        that.next().children(".custom-stepper-div").show("slow");
    }

    for(let i=0; i<myjson.dpts.length; i++){
        let dpt_pk = myjson.dpts[i],
            dpt_name = 'dpt_' + dpt_pk;

            
            myjson.dpts_dict[dpt_pk].mandatory = $("#" + dpt_name + '_mandatory').prop("checked");
            myjson.dpts_dict[dpt_pk].default = $("#" + dpt_name + '_default').val();
    }

    if(myjson.dpts.length > 0) {
        $("#custom_submit_btn").prop("disabled", false);
    } else {
        $("#custom_submit_btn").prop("disabled", true);
    }

    localStorage.setItem(itemkey, JSON.stringify(myjson));


}

function CustomChipsetDptsAddBtn() {

    
    // datapoints add button
    $(".custom-dpt-add-btn").on("click", function(){
        
        let itemkey: string = "chipset_specs";
        let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
        // let reqspan = $(this).siblings("span");
        let reqspan = $(this);

        let dpt_name = 'dpt_' + reqspan.attr("data-dpt_pk"),
            reqspan_helptext = reqspan.attr("title"),
            reqspan_options = reqspan.attr("data-options"),
            name = reqspan.html(),
            dpt_pk = reqspan.attr("data-dpt_pk");
        
        if ($("#custom_chipset_table_tbody").children('tr[data-pk="' + dpt_pk + '"]').length > 0) {
            alert("Selected datapoint type already exist");
            return;
        }

        let htmlstr = '<tr data-pk="' + dpt_pk + '">'; 
            htmlstr += '<td><h6><strong>' + name + '</strong></h6><input type="hidden" id="' + dpt_name + '_pk" value="' + dpt_pk + '"></td>';
            htmlstr += '<td><div class="custom-control custom-checkbox"><input type="checkbox" class="custom-control-input" id="' + dpt_name + '_mandatory"><label class="custom-control-label" for="' + dpt_name + '_mandatory"></label></div></td>';
            htmlstr += '<td class="md-form"><input type="text" id="' + dpt_name + '_default" class="form-control" value="">';
            if( reqspan_options !== "" ) {
                htmlstr += '<small>options: ' + reqspan_options + '</small>';
            }
            if(reqspan_helptext !== "") {
                if( reqspan_options != "") {
                    htmlstr += '<br/>';
                }
                htmlstr += '<small>helptext: ' + reqspan_helptext + '</small>';
            }
            htmlstr += '</td>';
            htmlstr += '<td><a class="text-danger custom-datapointtypes-li-delete-btn" data-name="' + dpt_name + '" data-dpt_pk="' + dpt_pk + '" onclick="CustomChipsetDptsRemoveBtn(this);"><i class="fas fa-times"></i></a></td>';
            htmlstr += '</tr>';

            myjson.dpts.push(dpt_pk);
            myjson.dpts_dict[dpt_pk] = {'pk' : dpt_pk, 'name' : reqspan.html(), 'options' : reqspan_options, 'helptext' : reqspan_helptext, 'mandatory': false,'default': ""};
            localStorage.setItem(itemkey, JSON.stringify(myjson));

        $("#custom_chipset_table_tbody").append(htmlstr);

        if(myjson.dpts.length > 0) {
            $("#custom_submit_btn").prop("disabled", false);
        } else {
            $("#custom_submit_btn").prop("disabled", true);
        }
    });
}

function CustomChipsetDptsRemoveBtn (that: string) {
    let itemkey: string = "chipset_specs";
    let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
 
    let dpt_pk: any = $(that).parents("tr").attr("data-pk");
 
    $(that).parents("tr").remove();
    let dpt_list_index: number = myjson.dpts.indexOf(dpt_pk);
    myjson.dpts.splice(dpt_list_index, 1);
    delete (myjson.dpts_dict[dpt_pk]);
    localStorage.setItem(itemkey, JSON.stringify(myjson));

    if(myjson.dpts.length > 0) {
        $("#custom_submit_btn").prop("disabled", false);
    } else {
        $("#custom_submit_btn").prop("disabled", true);
    }

}

function SetLatestProject(project_pk: string, user_pk: string) {
    if(project_pk) {
        localStorage.setItem('latest_project_id', project_pk);
        localStorage.setItem('latest_project_user', user_pk);
    }
}

function ProjectRedirectFunc(project_redirect: string, first_project_id: string) {

    if(project_redirect == "true") {
        let latest_project_id: string = localStorage.getItem('latest_project_id') || '';
        let latest_project_user: string = localStorage.getItem('latest_project_user') || '';

        if("{{user.pk}}" == latest_project_user) {
            if(latest_project_id) {
                // window.location.href = "{% url 'projects_view_user' %}/" + latest_project_id + "/patients";
                return(latest_project_id);
            } else {
                localStorage.removeItem('latest_project_id');
                localStorage.removeItem('latest_project_user');
                // window.location.href = "{% url 'index' %}";
                return(false);
            }
        } else {
            if(first_project_id) {
                // window.location.href = "{% url 'projects_view_user' %}/" + first_project_id + "/patients";
                return(first_project_id);
            } else {
                localStorage.removeItem('latest_project_id');
                localStorage.removeItem('latest_project_user');
                // window.location.href = "{% url 'index' %}";
                return(false);
            }
        }
    }

}


// patient specification
function PatientSpecificationGetStorage(project_pk: string){
    let itemkey: string = "patient_specs";
    let myjsondef: { [index: string]: any } = {
        "project_pk": project_pk,
        "dpts": [],
        "dpts_dict": {}
    }

    // let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
    let myjson: { [index: string]: any } = JSON.parse("{}");
    if (Object.keys(myjson).length === 0) {
        localStorage.setItem(itemkey, JSON.stringify(myjsondef));
        return;
    }

    // project_pk
    if (myjson.project_pk !== project_pk) {
        localStorage.setItem(itemkey, JSON.stringify(myjsondef));
        return;
    }

    // adding datapoints
    $.each(myjson.dpts, function(i, val){
        // add htmlstr to #custom_chipset_dpts_body
        let dpt_pk = val,
            name = myjson.dpts_dict[dpt_pk].name,
            dpt_name = 'dpt_' + dpt_pk,
            reqspan_helptext = myjson.dpts_dict[dpt_pk].helptext,
            reqspan_options = myjson.dpts_dict[dpt_pk].options,
            mandatory = myjson.dpts_dict[dpt_pk].mandatory,
            default_val = myjson.dpts_dict[dpt_pk].default;


        let htmlstr = '<tr data-pk="' + dpt_pk + '">'; 
            htmlstr += '<td><h6><strong>' + name + '</strong></h6><input type="hidden" id="' + dpt_name + '_pk" value="' + dpt_pk + '"></td>';
            htmlstr += '<td><div class="custom-control custom-checkbox"><input type="checkbox" class="custom-control-input" id="' + dpt_name + '_mandatory"><label class="custom-control-label" for="' + dpt_name + '_mandatory"></label></div></td>';
            htmlstr += '<td class="md-form"><input type="text" id="' + dpt_name + '_default" class="form-control" value="">';
            if( reqspan_options !== "" ) {
                htmlstr += '<small>options: ' + reqspan_options + '</small>';
            }
            if(reqspan_helptext !== "") {
                if( reqspan_options != "") {
                    htmlstr += '<br/>';
                }
                htmlstr += '<small>helptext: ' + reqspan_helptext + '</small>';
            }
            htmlstr += '</td>';
            htmlstr += '<td><a class="text-danger custom-datapointtypes-li-delete-btn" data-name="' + dpt_name + '" data-dpt_pk="' + dpt_pk + '" onclick="CustomChipsetDptsRemoveBtn(this);"><i class="fas fa-times"></i></a></td>';
            htmlstr += '</tr>';
            $("#custom_chipset_table_tbody").append(htmlstr);

            $("#" + dpt_name + '_mandatory').prop("checked", mandatory);
            $("#" + dpt_name + '_default').val(default_val);

    });

    if(myjson.dpts.length > 0) {
        $("#custom_submit_btn").prop("disabled", false);
    } else {
        $("#custom_submit_btn").prop("disabled", true);
    }

}


function CustomPatientDptsRemoveBtn (that: string) {
    let itemkey: string = "patient_specs";
    let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
 
    let dpt_pk: any = $(that).parents("tr").attr("data-pk");
 
    $(that).parents("tr").remove();
    let dpt_list_index: number = myjson.dpts.indexOf(dpt_pk);
    myjson.dpts.splice(dpt_list_index, 1);
    delete (myjson.dpts_dict[dpt_pk]);
    localStorage.setItem(itemkey, JSON.stringify(myjson));

    if(myjson.dpts.length > 0) {
        $("#custom_submit_btn").prop("disabled", false);
    } else {
        $("#custom_submit_btn").prop("disabled", true);
    }

}


function PatientDptsAddBtn() {

    // datapoints add button
    $(".custom-dpt-add-btn").on("click", function(){
        
        let itemkey: string = "patient_specs";
        let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
        // let reqspan = $(this).siblings("span");
        let reqspan = $(this);

        let dpt_name = 'dpt_' + reqspan.attr("data-dpt_pk"),
            reqspan_helptext = reqspan.attr("title"),
            reqspan_options = reqspan.attr("data-options"),
            name = reqspan.html(),
            dpt_pk = reqspan.attr("data-dpt_pk");
        
        if ($("#custom_patientspec_table_tbody").children('tr[data-pk="' + dpt_pk + '"]').length > 0) {
            alert("Selected datapoint type already exist");
            return;
        }

        let htmlstr = '<tr data-pk="' + dpt_pk + '">'; 
            htmlstr += '<td><h6><strong>' + name + '</strong></h6><input type="hidden" id="' + dpt_name + '_pk" value="' + dpt_pk + '"></td>';
            htmlstr += '<td><div class="custom-control custom-checkbox"><input type="checkbox" class="custom-control-input" id="' + dpt_name + '_mandatory"><label class="custom-control-label" for="' + dpt_name + '_mandatory"></label></div></td>';
            htmlstr += '<td class="md-form"><input type="text" id="' + dpt_name + '_default" class="form-control" value="">';
            if( reqspan_options !== "" ) {
                htmlstr += '<small>options: ' + reqspan_options + '</small>';
            }
            if(reqspan_helptext !== "") {
                if( reqspan_options != "") {
                    htmlstr += '<br/>';
                }
                htmlstr += '<small>helptext: ' + reqspan_helptext + '</small>';
            }
            htmlstr += '</td>';
            htmlstr += '<td><a class="text-danger custom-datapointtypes-li-delete-btn" data-name="' + dpt_name + '" data-dpt_pk="' + dpt_pk + '" onclick="CustomPatientDptsRemoveBtn(this);"><i class="fas fa-times"></i></a></td>';
            htmlstr += '</tr>';

            myjson.dpts.push(dpt_pk);
            myjson.dpts_dict[dpt_pk] = {'pk' : dpt_pk, 'name' : reqspan.html(), 'options' : reqspan_options, 'helptext' : reqspan_helptext, 'mandatory': false,'default': ""};
            localStorage.setItem(itemkey, JSON.stringify(myjson));

        $("#custom_patientspec_table_tbody").append(htmlstr);

        if(myjson.dpts.length > 0) {
            $("#custom_submit_btn").prop("disabled", false);
        } else {
            $("#custom_submit_btn").prop("disabled", true);
        }
    });

}


// sample specification
function SampleSpecificationGetStorage(project_pk: string){
    let itemkey: string = "sample_specs";
    let myjsondef: { [index: string]: any } = {
        "project_pk": project_pk,
        "dpts": [],
        "dpts_dict": {}
    }

    // let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
    let myjson: { [index: string]: any } = JSON.parse("{}");
    if (Object.keys(myjson).length === 0) {
        localStorage.setItem(itemkey, JSON.stringify(myjsondef));
        return;
    }

    // project_pk
    if (myjson.project_pk !== project_pk) {
        localStorage.setItem(itemkey, JSON.stringify(myjsondef));
        return;
    }

    // adding datapoints
    $.each(myjson.dpts, function(i, val){
        // add htmlstr to #custom_chipset_dpts_body
        let dpt_pk = val,
            name = myjson.dpts_dict[dpt_pk].name,
            dpt_name = 'dpt_' + dpt_pk,
            reqspan_helptext = myjson.dpts_dict[dpt_pk].helptext,
            reqspan_options = myjson.dpts_dict[dpt_pk].options,
            mandatory = myjson.dpts_dict[dpt_pk].mandatory,
            default_val = myjson.dpts_dict[dpt_pk].default;


        let htmlstr = '<tr data-pk="' + dpt_pk + '">'; 
            htmlstr += '<td><h6><strong>' + name + '</strong></h6><input type="hidden" id="' + dpt_name + '_pk" value="' + dpt_pk + '"></td>';
            htmlstr += '<td><div class="custom-control custom-checkbox"><input type="checkbox" class="custom-control-input" id="' + dpt_name + '_mandatory"><label class="custom-control-label" for="' + dpt_name + '_mandatory"></label></div></td>';
            htmlstr += '<td class="md-form"><input type="text" id="' + dpt_name + '_default" class="form-control" value="">';
            if( reqspan_options !== "" ) {
                htmlstr += '<small>options: ' + reqspan_options + '</small>';
            }
            if(reqspan_helptext !== "") {
                if( reqspan_options != "") {
                    htmlstr += '<br/>';
                }
                htmlstr += '<small>helptext: ' + reqspan_helptext + '</small>';
            }
            htmlstr += '</td>';
            htmlstr += '<td><a class="text-danger custom-datapointtypes-li-delete-btn" data-name="' + dpt_name + '" data-dpt_pk="' + dpt_pk + '" onclick="CustomChipsetDptsRemoveBtn(this);"><i class="fas fa-times"></i></a></td>';
            htmlstr += '</tr>';
            $("#custom_chipset_table_tbody").append(htmlstr);

            $("#" + dpt_name + '_mandatory').prop("checked", mandatory);
            $("#" + dpt_name + '_default').val(default_val);

    });

    if(myjson.dpts.length > 0) {
        $("#custom_submit_btn").prop("disabled", false);
    } else {
        $("#custom_submit_btn").prop("disabled", true);
    }

}


function CustomSampleDptsRemoveBtn (that: string) {
    let itemkey: string = "sample_specs";
    let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
 
    let dpt_pk: any = $(that).parents("tr").attr("data-pk");
 
    $(that).parents("tr").remove();
    let dpt_list_index: number = myjson.dpts.indexOf(dpt_pk);
    myjson.dpts.splice(dpt_list_index, 1);
    delete (myjson.dpts_dict[dpt_pk]);
    localStorage.setItem(itemkey, JSON.stringify(myjson));

    if(myjson.dpts.length > 0) {
        $("#custom_submit_btn").prop("disabled", false);
    } else {
        $("#custom_submit_btn").prop("disabled", true);
    }

}


function SampleDptsAddBtn() {

    // datapoints add button
    $(".custom-dpt-add-btn").on("click", function(){
        
        let itemkey: string = "sample_specs";
        let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");
        // let reqspan = $(this).siblings("span");
        let reqspan = $(this);

        let dpt_name = 'dpt_' + reqspan.attr("data-dpt_pk"),
            reqspan_helptext = reqspan.attr("title"),
            reqspan_options = reqspan.attr("data-options"),
            name = reqspan.html(),
            dpt_pk = reqspan.attr("data-dpt_pk");
        
        if ($("#custom_samplespec_table_tbody").children('tr[data-pk="' + dpt_pk + '"]').length > 0) {
            alert("Selected datapoint type already exist");
            return;
        }

        let htmlstr = '<tr data-pk="' + dpt_pk + '">'; 
            htmlstr += '<td><h6><strong>' + name + '</strong></h6><input type="hidden" id="' + dpt_name + '_pk" value="' + dpt_pk + '"></td>';
            htmlstr += '<td><div class="custom-control custom-checkbox"><input type="checkbox" class="custom-control-input" id="' + dpt_name + '_mandatory"><label class="custom-control-label" for="' + dpt_name + '_mandatory"></label></div></td>';
            htmlstr += '<td class="md-form"><input type="text" id="' + dpt_name + '_default" class="form-control" value="">';
            if( reqspan_options !== "" ) {
                htmlstr += '<small>options: ' + reqspan_options + '</small>';
            }
            if(reqspan_helptext !== "") {
                if( reqspan_options != "") {
                    htmlstr += '<br/>';
                }
                htmlstr += '<small>helptext: ' + reqspan_helptext + '</small>';
            }
            htmlstr += '</td>';
            htmlstr += '<td><a class="text-danger custom-datapointtypes-li-delete-btn" data-name="' + dpt_name + '" data-dpt_pk="' + dpt_pk + '" onclick="CustomSampleDptsRemoveBtn(this);"><i class="fas fa-times"></i></a></td>';
            htmlstr += '</tr>';

            myjson.dpts.push(dpt_pk);
            myjson.dpts_dict[dpt_pk] = {'pk' : dpt_pk, 'name' : reqspan.html(), 'options' : reqspan_options, 'helptext' : reqspan_helptext, 'mandatory': false,'default': ""};
            localStorage.setItem(itemkey, JSON.stringify(myjson));

        $("#custom_samplespec_table_tbody").append(htmlstr);

        if(myjson.dpts.length > 0) {
            $("#custom_submit_btn").prop("disabled", false);
        } else {
            $("#custom_submit_btn").prop("disabled", true);
        }
    });

}

function PatientSpecificationSetStorage(project_pk: string) {
    let itemkey: string = "patient_specs";
    let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");

    if (Object.keys(myjson).length === 0) {
        PatientSpecificationGetStorage(project_pk);
        return;
    }

    // project_pk
    if (myjson.project_pk !== project_pk) {
        PatientSpecificationGetStorage(project_pk);
        return;
    }

    for(let i=0; i<myjson.dpts.length; i++){
        let dpt_pk = myjson.dpts[i],
            dpt_name = 'dpt_' + dpt_pk;

            
            myjson.dpts_dict[dpt_pk].mandatory = $("#" + dpt_name + '_mandatory').prop("checked");
            myjson.dpts_dict[dpt_pk].default = $("#" + dpt_name + '_default').val();
    }

    if(myjson.dpts.length > 0) {
        $("#custom_submit_btn").prop("disabled", false);
    } else {
        $("#custom_submit_btn").prop("disabled", true);
    }

    localStorage.setItem(itemkey, JSON.stringify(myjson));


}


function SampleSpecificationSetStorage(project_pk: string) {
    let itemkey: string = "sample_specs";
    let myjson: { [index: string]: any } = JSON.parse(localStorage.getItem(itemkey) || "{}");

    if (Object.keys(myjson).length === 0) {
        SampleSpecificationGetStorage(project_pk);
        return;
    }

    // project_pk
    if (myjson.project_pk !== project_pk) {
        SampleSpecificationGetStorage(project_pk);
        return;
    }

    for(let i=0; i<myjson.dpts.length; i++){
        let dpt_pk = myjson.dpts[i],
            dpt_name = 'dpt_' + dpt_pk;

            
            myjson.dpts_dict[dpt_pk].mandatory = $("#" + dpt_name + '_mandatory').prop("checked");
            myjson.dpts_dict[dpt_pk].default = $("#" + dpt_name + '_default').val();
    }

    if(myjson.dpts.length > 0) {
        $("#custom_submit_btn").prop("disabled", false);
    } else {
        $("#custom_submit_btn").prop("disabled", true);
    }

    localStorage.setItem(itemkey, JSON.stringify(myjson));


}

function custom_pagination(page:string) {
    var href = new URL(window.location.href);
    href.searchParams.set("page", page);
    window.location.href = href.href;
}