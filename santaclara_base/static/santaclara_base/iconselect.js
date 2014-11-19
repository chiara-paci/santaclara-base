$(document).ready(function(){

    $(".santaclaraiconselect").click(function(event){
	event.preventDefault();
	var value=$(this).data("value");
	var target_view=$(this).data("target_view");
	var target_input=$(this).data("target_input");
	var text=$(this).html();

	$("#"+target_input).val(value);
	$("#"+target_view).html(text);

	$("ul.santaclaraiconselectul li.selected").removeClass("selected");
	$(this).parent().addClass("selected");
	$(this).parent().parent().hide();
    });

    $(".santaclaraiconselectothers").click(function(event){
	event.preventDefault();
	var optionsarea_id=$(this).data("optionsarea_id");
	$("#"+optionsarea_id).toggle();
    });

    $("ul.santaclaraiconselectul").hide();

/*    $(".taginput").each(function(index){
	var open_tl=$(this).find("a.taglistopen").first();
	var close_tl=$(this).find("a.taglistclose").first();
	var div_tl=$(this).find(".taglist").first();

	open_tl.show();
	close_tl.hide();
	div_tl.hide();
	
	open_tl.click(function(event){
	    close_tl.show();
	    open_tl.hide();
	    div_tl.show();
	});
	
	close_tl.click(function(event){
	    close_tl.hide();
	    open_tl.show();
	    div_tl.hide();
	});
	
	$(".taglabel").click(function(event){
	    var label=$(this).html();
	    var widget_name=$(this).data("widget-name");
	    var entry_tl=$('#id_'+widget_name);
	    entry_tl.val(label);
	});
	
    });

*/

});
