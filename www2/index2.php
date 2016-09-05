<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Azimuth</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" >
    <meta name="viewport" content="width=device-width, initial-scale=1.0" >

    <!-- Google Fonts -->
    <link rel='stylesheet' type='text/css' href='http://fonts.googleapis.com/css?family=Roboto:400,900italic,700italic,900,700,500italic,500,400italic,300italic,300,100italic,100|Open+Sans:400,300,400italic,300italic,600,600italic,700italic,700,800|Source+Sans+Pro:400,200,200italic,300,300italic,400italic,600,600italic,700' >

    <!-- Styles -->
    <link rel='stylesheet' type='text/css' href="css/bootstrap.css" >
    <link rel='stylesheet' type='text/css' href="font-awesome/css/font-awesome.css" >
    <link rel='stylesheet' type='text/css' href="css/style.css" >
    <link rel='stylesheet' type='text/css' href="css/responsive.css" >
    <link rel='stylesheet' type='text/css' href="layerslider/css/layerslider.css" >
    <link rel='stylesheet' type='text/css' href="css/orange.css" title="orange" >

    <!-- Scripts -->
    <script src="js/jquery.1.9.1.js" type="text/javascript"></script>
    <!-- <script src='js/testimonials.js'></script> -->
    <script src='js/bootstrap.js'></script>
    <script src="js/html5lightbox.js"></script>
    <script src="js/jquery.carouFredSel-6.2.1-packed.js" type="text/javascript"></script>
    <script src='js/script.js'></script>
    <script defer src="js/jquery.flexslider.js"></script>
    <script defer src="js/jquery.mousewheel.js"></script>

    <!-- Scripts For Layer Slider  -->
    <script src="layerslider/js/greensock.js" type="text/javascript"></script>
    <!-- LayerSlider script files -->
    <script src="layerslider/js/layerslider.transitions.js" type="text/javascript"></script>
    <script src="layerslider/js/layerslider.kreaturamedia.jquery.js" type="text/javascript"></script>

    <script>
      $(document).ready(function(){
      jQuery("#layerslider").layerSlider({
      responsive: true,
      responsiveUnder: 1280,
      layersContainer: 1170,
      skin: 'fullwidth',
      hoverPrevNext: true,
      skinsPath: 'layerslider/skins/'
      });
      });
    </script>

    <script>
      $(window).load(function(){

      $('.stories-carousel').flexslider({
      animation: "slide",
      animationLoop: false,
      controlNav: false,	
      maxItems: 1,
      pausePlay: false,
      mousewheel:true,	
      start: function(slider){
      $('body').removeClass('loading');
      }
      });

      $('.footer_carousel').flexslider({
      animation: "slide",
      animationLoop: false,
      slideShow:false,
      controlNav: true,	
      maxItems: 1,
      pausePlay: false,
      mousewheel:true,
      start: function(slider){
      $('body').removeClass('loading');
      }
      });

      });
    </script>

    <!-- Script for smooth sliding -->
    <script>
    $(document).ready(function() {
    function filterPath(string) {
        return string
        .replace(/^\//,'')
        .replace(/(index|default).[a-zA-Z]{3,4}$/,'')
        .replace(/\/$/,'');
    }
    var locationPath = filterPath(location.pathname);
    var scrollElem = scrollableElement('html', 'body');

    $('a[href*=#]').each(function() {
        var thisPath = filterPath(this.pathname) || locationPath;
        if (  locationPath == thisPath
        && (location.hostname == this.hostname || !this.hostname)
        && this.hash.replace(/#/,'') ) {
        var $target = $(this.hash), target = this.hash;
            if (target) {
            var targetOffset = $target.offset().top;
        $(this).click(function(event) {
          event.preventDefault();
          $(scrollElem).animate({scrollTop: targetOffset}, 100, function() {
            location.hash = target;
          });
        });
      }
    }
  });

  // use the first element that is "scrollable"
  function scrollableElement(els) {
    for (var i = 0, argLength = arguments.length; i <argLength; i++) {
      var el = arguments[i],
          $scrollElement = $(el);
      if ($scrollElement.scrollTop()> 0) {
        return el;
      } else {
        $scrollElement.scrollTop(1);
        var isScrollable = $scrollElement.scrollTop()> 0;
        $scrollElement.scrollTop(0);
        if (isScrollable) {
          return el;
        }
      }
    }
    return [];
  }

});
    </script>

  </head>

  <body>
    <div class="theme-layout">

      <!-- Top Bar, Header, Menu, Logo -->
      <?php include("all_menu.php"); ?>

      <!-- Layer Slider -->
      <div id="layerslider-container-fw">

        <div id="layerslider" style="width: 100%; height: 530px; margin: 0px auto; ">

          <!-- Slide 1 -->
          <div class="ls-slide" data-ls="transition3d:53; timeshift:-1000;">			
            <img src="images/back_freetown.jpg" class="ls-bg" alt="Slide background">
            <h3 class="ls-l" style="top: 160px; left:130px; font-family:roboto; font-size:58px; font-weight:bold; color:#fff; line-height:60px; text-align:center;" data-ls="offsetxin:0;offsetyin:top;durationin:1500;delayin:1000;easingin:easeInOutQuart;fadein:false;scalexin:0;scaleyin:0;offsetxout:0;offsetyout:top;durationout:1000;fadeout:false;" >AFFORDABLE AND CLEAN <span>ENERGY</span></h3>

            <span class="ls-l slide3-subtitle2" style="top: 248px; left:130px; background:rgba(0,0,0,0.8); padding:13px; border-radius:3px; color:#fff; font-family:open sans; font-weight:900; font-size:26px; text-transform:uppercase; line-height:20px;" data-ls="offsetxin:0;offsetyin:bottom;durationin:1500;delayin:1300;easingin:easeInOutQuart;fadein:false;scalexin:0;scaleyin:0;offsetxout:0;offsetyout:top;durationout:1000;fadeout:false;">For <i style="font-style:normal;">Rural</i> and <i style="font-style:normal;">Peri-Urban</i> off-grid households</span>

            <span class="ls-l slide3-subtitle" style="top: 310px; left:800px; padding:13px; border-radius:3px; color:#fff; font-family:open sans; font-weight:900; font-size:26px; text-transform:uppercase; line-height:20px;" data-ls="offsetxin:0;offsetyin:bottom;durationin:1500;delayin:1200;easingin:easeInOutQuart;fadein:false;scalexin:0;scaleyin:0;offsetxout:0;offsetyout:top;durationout:1000;fadeout:false;">In <i style="font-style:normal; color:#373737;">Sierra Leone</i></span>
          </div>

          <!-- Slide 3 -->
          <div class="ls-slide" data-ls="transition3d:35;timeshift:-1000;">			
            <img src="images/back_village.jpg" class="ls-bg" alt="Slide background">

            <span class="ls-l slide1"	style="top: 196px; left:248px; font-family:roboto; font-size:24px; font-weight:600; color:#000; padding:10px 20px 10px 20px; background:rgba(255,255,255,0.9); border-radius:4px 0 0px 4px; border-left:2px solid #93b631; position:relative; line-height:22px; float:left;" data-ls="offsetxin:0;offsetyin:top;durationin:1000;easingin:easeOutQuad;fadein:false;rotatein:10;offsetxout:0;durationout:1500;">INNOVATIVE <i>SOLAR ENERGY</i> PRODUCTS</span>

            <p class="ls-l slide1"	style="top: 250px; left:248px; font-family:roboto; font-size:18px; color:#fefefe;" data-ls="delayin:1000; scalein:4; durationin : 1000;">We distribute <strong>lamps</strong> and <strong>solar systems</strong> with long term financing options...</br>...enabling low income households to access life changing technology</p>
          </div>

          <!-- Slide 4 -->
          <div class="ls-slide" data-ls="transition3d:75;timeshift:-1000;">			
            <img src="images/back_battery.jpg" class="ls-bg" alt="Slide background">

            <h3 class="ls-l slide4" style="top:180px; left:150px; background:rgba(0,0,0,0.9); font-family:roboto; font-size:28px; font-weight:bold; color:#fefefe; padding:20px 60px 20px; border-radius:4px;" data-ls="offsetxin:bottom;durationin:500;delayin:1000;easingin:easeInOutQuart;fadein:false;scalexin:100;scaleyin:0;offsetxout:right;durationout:1400;fadeout:false;">
              <i>650 million</i> people lack access to electricity in sub-Saharan Africa</h3>

            <span class="ls-l slide4-subtitle" style="top:280px; left:215px;border-radius: 4px 4px 0 0; color: #FFFFFF;font-family: open sans;font-size: 13px;font-weight: bold; padding: 5px 10px;" data-ls="offsetxin:bottom;durationin:500;delayin:2000;easingin:easeInOutQuart;fadein:false;scalexin:100;scaleyin:0;offsetxout:right;durationout:1400;fadeout:false;">Want To Help? Join The <a style="color:white" href="https://www.lightingafrica.org/">Power For All</a> Campaign</span>
          </div>

        </div>
      </div>

      <!-- Our Project -->
      <section id="project" class="block">
      <div class="container">
        <div class="row">
          <div class="col-md-12">
            <div class="sec-heading">
              <h2><strong>Our</strong> Project</h2>
            </div><!-- Section Title -->
            <div class="our-project-box">
              <div class="row">
                <div class="col-md-4">
                  <div class="row">
                    <div class="col-md-5">
                      <div class="icon-box">
                        <i class="icon-sun"></i>
                        <div class="need">
                          <p>LEARN <span>MORE</span></p>
                          <a href="http://www.powerforall.org" title="">...</a>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-7">
                      <div class="project-detail">
                        <a>Solar Energy</a>
                        <p>We distribute solar lamps to fight widespread energy poverty in Sierra Leone.</p>			
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="row">
                    <div class="col-md-5">
                      <div class="icon-box">
                        <i class="icon-time"></i>
                        <div class="need">
                          <p>LEARN <span>MORE</span></p>
                          <a href="http://www.powerforall.org" title="">...</a>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-7">
                      <div class="project-detail">
                        <a>Durable Solution</a>
                        <p>Our batteries, solar panels and lights have a 5 year lifetime and deliver high quality lighting and energy.</p>			
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="row">
                    <div class="col-md-5">
                      <div class="icon-box">
                        <i class="icon-leaf"></i>
                        <div class="need">
                          <p>LEARN <span>MORE</span></p>
                          <a href="http://www.powerforall.org" title="">...</a>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-7">
                      <div class="project-detail">
                        <a>Environment benefits</a>
                        <p>Our products replace heavily polluting candles, kerosene lamps and cheap batteries.</p>			
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="row">
                    <div class="col-md-5">
                      <div class="icon-box">
                        <i class="icon-heart"></i>
                        <div class="need">
                          <p>LEARN <span>MORE</span></p>
                          <a href="http://www.powerforall.org" title="">...</a>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-7">
                      <div class="project-detail">
                        <a>Health Benefits</a>
                        <p>Solar lighting reduces indoor pollution, fire hazards and oil residues on food.</p>			
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="row">
                    <div class="col-md-5">
                      <div class="icon-box">
                        <i class="icon-dollar"></i>
                        <div class="need">
                          <p>LEARN <span>MORE</span></p>
                          <a href="http://www.powerforall.org" title="">...</a>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-7">
                      <div class="project-detail">
                        <a>Customer Savings</a>
                        <p>Our customers save money almost instantly thanks to low deposit costs and flexible repayment plans.</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="row">
                    <div class="col-md-5">
                      <div class="icon-box">
                        <i class="icon-bar-chart"></i>
                        <div class="need">
                          <p>LEARN <span>MORE</span></p>
                          <a href="http://www.powerforall.org" title="">...</a>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-7">
                      <div class="project-detail">
                        <a>Financial Inclusion</a>
                        <p>Asset ownership and credit scoring of payments helps our customers access basic Financial Services.</p>			
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      </section>	

      <!-- Welcome Message -->
      <section class="block remove-top" style="padding-bottom: 0px;">
      <div class="container">
        <div class="row">
          <div class="col-md-12">
            <div class="welcome-box">
              <h2>We Bring <strong>Capital</strong> And <strong>Technology</strong> Together To Finance A Solar Energy Revolution And Transform The Way People <strong>Live</strong>, <strong>Work</strong> and <strong>Play</strong>.</h2>
              <p>Help us finance the energy revolution in Sierra Leone.</p>
              <a href="contact.php"><span style="padding-left: 30px;padding-right: 30px;">Get Involved!</span></a>
            </div>
          </div>
        </div>
      </div>
      </section>

      <!-- Team -->
      <section id="team" class="block">
      <div class="container">
        <div class="row">
          <div class="col-md-12">
            <div class="sec-heading">
              <h2><strong>Our </strong><span>Team</span></h2>
            </div>
            <div class="staff">
              <div class="row">
                
                <div class="col-md-4">
                  <div class="staff-member">
                    <img src="images/head_nthabi.jpg" alt="" />
                    <div class="member-intro">
                      <h3>Nthabi Mosia</h3>
                      <span>Co-founder and CMO</span>
                    </div>
                    <div class="social-contacts">
                      <ul>
                        <li><a href="https://www.linkedin.com/in/nthabisengmosia" title="Nthabi"><img src="images/flat_linked-in.jpg" alt="" /></a></li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div class="col-md-4">
                  <div class="staff-member">
                    <img src="images/head_eric.jpg" alt="" />
                    <div class="member-intro">
                      <h3>Eric Silverman</h3>
                      <span>Co-founder and COO</span>
                    </div>
                    <div class="social-contacts">
                      <ul>
                        <li><a href="https://www.linkedin.com/in/ericmsilverman" title="Eric"><img src="images/flat_linked-in.jpg" alt="" /></a></li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div class="col-md-4">
                  <div class="staff-member">
                    <img src="images/head_alexandre.jpg" alt="" />
                    <div class="member-intro">
                      <h3>Alexandre Tourre</h3>
                      <span>Co-founder and CEO</span>
                    </div>
                    <div class="social-contacts">
                      <ul>
                        <li><a href="https://www.linkedin.com/in/alexandretourre" title="Alexandre"><img src="images/flat_linked-in.jpg" alt="" /></a></li>
                        <li><a href="http://tour.re" title="tour.re"><img src="images/flat_web.png" alt="" /></a></li>
                      </ul>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </div>
      </section>

      <!-- Support -->
      <section class="block remove-top">
      <div class="container">
        <div class="row">
          <div class="col-md-6">
            <div class="sec-heading">
              <h2><strong>They</strong> Support Us</h2>
            </div>
            <div class="stories-carousel">
              <ul class="slides">
                <li>
                <div class="row">
                  <div class="col-md-6">
                    <div class="story">
                      <div class="story-img">
                        <img src="images/logo_cbs.png" alt="" />
                        <h5>CBS Incubator</h5>
                        <a href="http://www8.gsb.columbia.edu/entrepreneurship/innovation/" title=""><span></span></a>
                      </div>
                      <p style="margin-bottom: 4px;">Innovation and Entrepreneurship @ Columbia is a cross-University program that nurtures and leverages ideas and technologies within Columbia University that have the potential to generate returns in the form of new products or services, processes, licensing revenues, and strategic alliances. </p>
                    </div><!-- Story -->
                  </div> 
                  <div class="col-md-6">
                    <div class="story">
                      <div class="story-img">
                        <img src="images/logo_dprize.png" alt="" />
                        <h5>D-Prize 2015 winner</h5>
                        <a href="http://www.d-prize.org/" title=""><span></span></a>
                      </div>
                      <p style="margin-bottom: 4px;">The D-Prize is a social venture competition targeting poverty problems. Azimuth won a $20,000 grant as the 2015 prize in the Solar Lamp and Energy category. The D-Prize's network of experts and former winners now supports Azimuth in its development in West Africa. </p>
                    </div><!-- Story -->
                  </div>
                </div>
                </li>
                <li>
                <div class="row">
                  <div class="col-md-6">
                    <div class="story">
                      <div class="story-img">
                        <img src="images/logo_sipa.png" alt="" />
                        <h5>SIPA Entrepreneurship</h5>
                        <a href="https://sipa.columbia.edu/challenge-grant" title=""><span></span></a>
                      </div>
                      <p style="margin-bottom: 4px;">Azimuth Solar won the First Prize in Columbia University’s School of International and Public Affairs' entrepreneurship challenge. During 8 months, Azimuth competed with over 15 other teams, receiving the support of SIPA's network and more than $40,000 of grants in the process. </p>
                    </div><!-- Story -->
                  </div>
                  <div class="col-md-6">
                    <div class="story">
                      <div class="story-img">
                        <img src="images/logo_hult.jpg" alt="" />
                        <h5>Hult Prize 2016</h5>
                        <a href="http://www.hultprize.org/" title=""><span></span></a>
                      </div>
                      <p style="margin-bottom: 4px;">The Hult Prize Foundation is a start-up accelerator for budding young social entrepreneurs emerging from the world’s universities. Lead by Muhammad Yunus and Bill Clinton, the planst's largest student competition will reward the winner with $1,000,000 in grant funding. </p>
                    </div><!-- Story -->
                  </div>
                </div>
                </li>
              </ul>
            </div>
          </div>

          <!-- News -->
          <div class="col-md-6">
            <div class="sec-heading">
              <h2><strong>Recent</strong> News</h2>
            </div>	<!-- Section Title -->
            <div class="row">
              <div class="col-md-12">
                <div class="recent-event">
                  <div class="recent-event-img">
                    <img src="images/newstop_video.png" alt="" />
                    <a class="html5lightbox" href="http://player.vimeo.com/video/157193611?color=ffffff" title="Azimuth Solar realeases its promotional video!"><span><i class="icon-play"></i></span></a>
                  </div>
                  <h4><a href="https://vimeo.com/157193611" title="">Introduction to Azimuth Solar</a></h4>
                  <ul>
                    <li><a href="#" title=""><i class="icon-user"></i>by alexandre tourre</a></li>
                    <li><a href="#" title=""><i class="icon-map-marker"></i>in New York City</a></li>
                    <li><a href="#" title=""><i class="icon-calendar-empty"></i><span>February</span> 28, 2016</a></li>
                  </ul>
                </div><!-- Latest Event -->
              </div>
              <div class="col-md-6">
                <div class="recent-event previous-event">
                  <div class="recent-event-img">
                    <img src="images/newsbot_datascience.jpg" alt="" />
                    <a href="http://datascience.columbia.edu/bringing-affordable-renewable-lighting-sierra-leone" title=""><span><i class="icon-play"></i></span></a>
                  </div>
                  <h4><a href="http://datascience.columbia.edu/bringing-affordable-renewable-lighting-sierra-leone" title="">Azimuth featured by Columbia's Data Science Institute</a></h4>
                  <ul>
                    <!--<li><a href="#" title=""><i class="icon-map-marker"></i>in South africa</a></li>-->
                    <li><a href="#" title=""><i class="icon-calendar-empty"></i><span>February</span> 22, 2016</a></li>
                  </ul>
                </div>
                <!-- Previous Event -->
              </div>
              <div class="col-md-6">
                <div class="recent-event  previous-event">
                  <div class="recent-event-img">
                    <img src="images/newsbot_survey.png" alt="" />
                    <a href="#" title=""><span><i class="icon-play"></i></span></a>
                  </div>
                  <h4><a href="single-post-image.html" title="">Azimuth Solar performs a 1,500 customers survey on Energy use</a></h4>
                  <ul>
                    <!--<li><a href="#" title=""><i class="icon-map-marker"></i>in South africa</a></li>-->
                    <li><a href="#" title=""><i class="icon-calendar-empty"></i><span>January</span> 16, 2016</a></li>
                  </ul>
                </div>
                <!-- Previous Event -->
              </div>
            </div>
          </div>
        </div>
      </div>
      </section>
    </div>

    <!-- Footer -->
    <?php include("all_footer.php"); ?>

  </body>
</html>
