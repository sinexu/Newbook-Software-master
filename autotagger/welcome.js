function filetype_chosen() {
	var inputlist = document.getElementsByClassName('uploadfile');
	for (var i = 0; i < inputlist.length; i++) {
		if (inputlist[i].checked) {
			document.getElementById(inputlist[i].value+"file").style.display="block";
		} else {
			document.getElementById(inputlist[i].value+"file").style.display="none";
		}
	}
}