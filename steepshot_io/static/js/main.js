function tgmenu() {
    document.getElementById("tgmenu").classList.toggle('change');
    document.getElementById("menu").classList.toggle('changem');
}

function fpg() {
    document.getElementById("mimg").classList.remove('mimg');
    document.getElementById("mimg2").classList.remove('mimg2');
    document.getElementById("mimg3").classList.remove('mimg3');
    document.getElementById("mimga").classList.remove('mimga');
    document.getElementById("panel1").classList.add('hd');
    document.getElementById("panel3").classList.add('hd');
    document.getElementById("panel2").classList.remove('hd');
    document.getElementById("buttons").classList.add('btpg2');
    document.getElementById("hmi").setAttribute("onClick", "spgr()");
    document.getElementById("contr").setAttribute("onClick", "spg()");
}

function spg() {
    document.getElementById("panel2").classList.add('hd');
    document.getElementById("panel1").classList.add('hd');
    document.getElementById("panel3").classList.remove('hd');
    document.getElementById("buttons").classList.add('hd');
    document.getElementById( "contr" ).setAttribute( "onClick", "tpg()" );
    document.getElementById( "hmi" ).setAttribute( "onClick", "tpgr()" );
}

function tpg(){
    document.getElementById("mimg").classList.add('mimg');
    document.getElementById("mimg2").classList.add('mimg2');
    document.getElementById("mimg3").classList.add('mimg3');
    document.getElementById("mimga").classList.add('mimga');
    document.getElementById("panel1").classList.remove('hd');
    document.getElementById("panel2").classList.add('hd');
    document.getElementById("panel3").classList.add('hd');
    document.getElementById("buttons").classList.remove('btpg2');
    document.getElementById( "hmi" ).removeAttribute("onClick");
    document.getElementById("buttons").classList.remove('hd');
    document.getElementById( "contr" ).setAttribute( "onClick", "fpg()" );
}

function fpgr() {
    document.getElementById("panel2").classList.add('hd');
    document.getElementById("panel1").classList.add('hd');
    document.getElementById("panel3").classList.remove('hd');
    document.getElementById("buttons").classList.add('hd');
    document.getElementById("buttons").classList.add('btpg2');
    document.getElementById( "hmi" ).setAttribute( "onClick", "tpgr()" );
    document.getElementById("mimg").classList.remove('mimg');
    document.getElementById("mimg2").classList.remove('mimg2');
    document.getElementById("mimg3").classList.remove('mimg3');
    document.getElementById("mimga").classList.remove('mimga');
}

function spgr() {
    document.getElementById("mimg").classList.add('mimg');
    document.getElementById("mimg2").classList.add('mimg2');
    document.getElementById("mimg3").classList.add('mimg3');
    document.getElementById("mimga").classList.add('mimga');
    document.getElementById("panel1").classList.remove('hd');
    document.getElementById("panel2").classList.add('hd');
    document.getElementById("panel3").classList.add('hd');
    document.getElementById("buttons").classList.remove('btpg2');
    document.getElementById( "hmi" ).setAttribute( "onClick", "fpgr()" );
}

function tpgr () {
    document.getElementById("panel2").classList.remove('hd');
    document.getElementById("panel3").classList.add('hd');
    document.getElementById("panel1").classList.add('hd');
    document.getElementById("buttons").classList.remove('hd');
    document.getElementById( "hmi" ).setAttribute( "onClick", "spgr()" );
}

function fpfp() {
    document.getElementById( "backtext" ).setAttribute( "style", "display:none;" );
    document.getElementById( "frontext" ).setAttribute( "style", "opacity:1;" );
    document.getElementById( "buttons" ).setAttribute( "style", "display:block;" );
    document.getElementById( "mimg").setAttribute( "style", "opacity:0 !important;" );
    document.getElementById( "mimg2").setAttribute( "style", "opacity:0 !important;" );
    document.getElementById(  "mimg3" ).setAttribute( "style", "opacity:0 !important;" );
}

function spfp() {
    document.getElementById( "backtext" ).removeAttribute( "style" );
    document.getElementById( "frontext" ).removeAttribute( "style" );
}

function tl() {
    var x = document.activeElement.id;
    var y = document.getElementById("id_email").value;

    if (x == "id_email") {
        document.getElementById( "textfield" ).classList.add('active');
        x=0;
    } else {
        if(y == "") {
            document.getElementById( "textfield" ).classList.remove('active');
            x=0;
        }
    }
}

var isMobile = window.matchMedia("(max-width: 767px)"); /*определяем мобильный телефон*/
var isTablet=window.matchMedia("(min-width: 768px) and (max-width: 1024px)");

if(isMobile.matches||isTablet.matches){
    document.getElementById( "hmi" ).removeAttribute( "onclick()");
    /* script for touch */
    window.addEventListener('load', function(){
        var initialPoint;
        var finalPoint;
        var p1 = "1";

        document.addEventListener('touchstart', function(event) {
            event.preventDefault();
            event.stopPropagation();
            initialPoint=event.changedTouches[0];
        }, false);

        document.addEventListener('touchend', function(event) {
            event.preventDefault();
            event.stopPropagation();
            finalPoint=event.changedTouches[0];
            var xAbs = Math.abs(initialPoint.pageX - finalPoint.pageX);

            if (xAbs > 8 ) {
                var isMobile = window.matchMedia("only screen and (max-width: 767px)"); /*определяем мобильный телефон/планшет*/
                
                if(isMobile.matches){
                    if (finalPoint.pageY < initialPoint.pageY){ /*вверх свайп*/
                        if (document.getElementById("panel3").className !== "hd"){
                            tpg();
                            p1="1";
                            document.getElementById( "mimg").removeAttribute( "style");
                            document.getElementById( "mimg2").removeAttribute( "style");
                            document.getElementById(  "mimg3" ).removeAttribute( "style");
                        } else {
                            if (document.getElementById("panel2").className !== "hd"){
                                spg();
                                document.getElementById( "buttons" ).removeAttribute( "style");
                            }

                            if (document.getElementById("panel1").className !== "hd" ){
                                function firstP(){
                                    if(p1=="2"){
                                        spfp();
                                        fpg();
                                    } else {
                                        function secondP() {
                                            if (p1=="1"){
                                                fpfp();
                                                p1="2";
                                            }
                                        }
                                        
                                        secondP();
                                    }
                                }
                                        
                                firstP();
                            }
                        }
                    } else {
                        if (document.getElementById("panel1").className !== "hd") {
                            function firstPR(){
                                if(p1=="1"){
                                    fpgr();
                                    p1="2";
                                } else {
                                    function secondPR() {
                                        if (p1=="2"){
                                            spfp();
                                            document.getElementById( "buttons" ).removeAttribute( "style");
                                            document.getElementById( "mimg").removeAttribute( "style");
                                            document.getElementById( "mimg2").removeAttribute( "style");
                                            document.getElementById(  "mimg3" ).removeAttribute( "style");
                                            p1="1";
                                            document.getElementById( "hmi" ).removeAttribute( "onclick()");
                                        }
                                    }

                                    secondPR();
                                }
                            }
                            
                            firstPR();
                        } else {
                            if (document.getElementById("panel2").className !== "hd"){
                                fpfp();
                                spgr();
                            }

                            if (document.getElementById("panel3").className !== "hd"){
                                document.getElementById( "buttons" ).setAttribute( "style", "display:block;" );
                                tpgr();
                            }
                        }
                    }
                } else {
                    if (finalPoint.pageY < initialPoint.pageY){
                        if (document.getElementById("panel3").className !== "hd") {
                            tpg();
                        } else {
                            if (document.getElementById("panel2").className !== "hd"){
                                spg();
                            }

                            if (document.getElementById("panel1").className !== "hd"){
                                fpg();
                            }
                        }
                    } else {
                        if (document.getElementById("panel1").className !== "hd"){
                            fpgr();
                        } else {
                            if (document.getElementById("panel2").className !== "hd"){
                                spgr();
                            }
                            
                            if (document.getElementById("panel3").className !== "hd"){
                                tpgr();
                            }
                        }
                    }
                }
            }
        }, false);


        $('#header').bind('touchstart touchend touchup', function(event) {
            event.stopPropagation();
        });

        $('#id_email').bind('touchstart touchend touchup', function(event) {
            event.stopPropagation();
        });

        $('#soc_links').bind('touchstart touchend touchup', function(event) {
            event.stopPropagation();
        });

        $('.android').bind('touchstart touchend touchup', function(event) {
            event.stopPropagation();
        });

        $('.apple').bind('touchstart touchend touchup', function(event) {
            event.stopPropagation();
        });

        $('#submit').bind('touchstart touchend touchup', function(event) {
            event.stopPropagation();
        });
    });
} else {
    var sfd=1;

    function pdelay() {
        setTimeout(function spdad (){sfd=1;},800);
    }
    
    /* script for scroll  */
    $(window).on('wheel', function ws(event){
        var dm = event.originalEvent.deltaY;

        if(dm < 0){ /*scroll upх*/
            if (document.getElementById("panel1").className !== "hd" && sfd=="1"){
                sfd=0;
                fpgr();
                pdelay();
            } else {
                if (document.getElementById("panel2").className !== "hd" && sfd=="1") {
                    spgr();
                    sfd=0;
                    pdelay();
                } else {
                    if (document.getElementById("panel3").className !== "hd" && sfd=="1") {
                        tpgr();
                        sfd=0;
                        pdelay();
                    }
                }
            }
        } else  { /*scroll down*/
            if(document.getElementById("panel3").className !== "hd" && sfd=="1"){
                sfd=0;
                tpg();
                pdelay();
            } else{
                if (document.getElementById("panel2").className !== "hd" && sfd=="1"){
                    sfd=0;
                    spg();
                    pdelay();
                } else {
                    if (document.getElementById("panel1").className !== "hd"&& sfd=="1"){
                        fpg();
                        pdelay();
                        sfd=0;
                    }

                    fPageDw();
                }
            }
        }
    });

    /*script for button*/
    document.onkeydown = checkKey;


    function checkKey(a) {
        a = a || window.event;

        if (a.keyCode == '38' || a.keyCode == '37') {
                // up and to the left

            if (document.getElementById("panel1").className !== "hd") {
                fpgr();
            } else {
                function tPageUp() {
                    if (document.getElementById("panel2").className !== "hd") {
                        spgr();
                    } else {
                        function sPageUp() {
                            if (document.getElementById("panel3").className !== "hd") {
                                tpgr(); }
                            }

                        function sdelay() {sPageUp()}/* не удалять! без него пропускает страницы*/
                        setTimeout(sdelay,10);
                    }
                }
                    
                tPageUp();
            }
        } else if (a.keyCode == '40'||a.keyCode == '39') {
            // down and to the right
            if (document.getElementById("panel3").className !== "hd")
                {   tpg();}
            else {
                if (document.getElementById("panel2").className !== "hd"){
                    spg();
                } else {
                    function fPageDw() {
                        if (document.getElementById("panel1").className !== "hd"){
                            fpg();
                        }
                    }

                    function fdelay() {fPageDw()} /* не удалять! без него пропускает страницы*/
                    setTimeout(fdelay,10);
                }
            }
        }
    }
}