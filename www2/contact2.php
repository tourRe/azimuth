<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Azimuth - Contact</title>
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
    <script 
      src="js/jquery.1.9.1.js" type="text/javascript"> </script>
    <script 
      src='js/testimonials.js'> </script>
    <script 
      src='js/bootstrap.js'> </script>
    <script 
      src="js/html5lightbox.js"> </script>
    <script 
      src="js/jquery.carouFredSel-6.2.1-packed.js" type="text/javascript"> </script>
    <script 
      src='js/script.js'> </script>
    <script 
      defer src="js/jquery.flexslider.js"> </script>
    <script 
      defer src="js/jquery.mousewheel.js"> </script>

  </head>

  <body>

    <!-- Top Bar, Header, Menu, Logo -->
    <?php include("all_menu.php"); ?>

    <!-- Top Image -->
    <div class="top-image">
      <img src="images/contact_photo.jpg" alt="" />
    </div>

    <section class="inner-page">
    <div class="container">

      <!-- Page Title -->
      <div class="page-title">
        <h1>Contact <span>Us</span></h1>
      </div>

      <!-- Contact Info and Map -->
      <div class="row">
        <div class="col-md-6">
          <div class="contact-info">
            <h3 class="sub-head">CONTACT INFORMATION</h3>
            <iframe width="600" height="450" frameborder="0" style="border:0"
              src="https://www.google.com/maps/embed/v1/place?q=place_id:ChIJQ_OrOhgGAQ8RGfcsx83paVM&key=AIzaSyDRPITQtMUgREl0dWhTcRJLxtkchVHkvbM"
              allowfullscreen></iframe>
            <p>Azimuth’s first target country is <strong>Sierra Leone</strong>, a ~6 million off-grid market with rapidly growing mobile money adoption. In Sierra Leone, Azimuth distributes high quality solar products and appliances under its local brand, <strong>Easy Solar</strong>.</p>
            <p>Whether you're simply looking for more <strong>information</strong>, interested in helping us <strong>finance</strong> the energy revolution, willing to <strong>volunteer</strong> or thinking of <strong>applying</strong> for a full-time position, we want to hear from you!</p>
            <ul class="contact-details">
              <li>
              <span><i class="icon-home"></i>ADDRESS</span>
              <p>1 Grand Army Plaza, Brooklyn, New York</p>
              </li>
              <li>
              <span><i class="icon-phone-sign"></i>PHONE NO</span>
              <p>(US) +1 917 548-6514 / (SL) +232 78 97 59 14</p>
              </li>
              <li>
              <span><i class="icon-envelope-alt"></i>EMAIL ID</span>
              <p>info@azimuth-solar.com</p>
              </li>
              <li>
              <span><i class="icon-link"></i>WEB ADDRESS</span>
              <p>http://www.azimuth-solar.com</p>
              </li>
            </ul>
          </div>
        </div>	

        <!-- Message Form -->
        <div class="col-md-6">
          <div id="message"></div>
          <div class="form">
            <h3 class="sub-head">CONTACT US BY MESSAGE</h3>
            <p>The following fields are required <span>*</span></p>
            <form method="post"  action="contact_send_message.php" name="contactform" id="contactform">
              <label for="name" accesskey="U">Full name <span>*</span></label>
              <input name="name" class="form-control input-field" type="text" id="name" size="30" value="" />
              <label for="email" accesskey="E">Email Address <span>*</span></label>
              <input name="email" class="form-control input-field" type="text" id="email" size="30" value="" />
              <label for="comments" accesskey="C">Message <span>*</span></label>
              <textarea name="comments" rows="9" id="comments" rows="7" class="form-control input-field"></textarea>
              <input type="submit" class="form-button submit" id="submit" value="SEND MESSAGE" />
            </form>
          </div>
        </div>	

      </div>	
    </div>	

    <div class="social-connect">	
      <div class="container">
        <h3>FIND US ON SOCIAL MEDIA.</h3>
        <ul class="social-bar">
          <li><a href="https://www.facebook.com/azimuthsolar"><img alt="" src="images/flat_facebook.jpg"></a></li>
          <li><a href="https://www.linkedin.com/company/10800217"><img alt="" src="images/flat_linked-in.jpg"></a></li>
          <li><a href="https://twitter.com/azimuthsolar"><img alt="" src="images/flat_twitter.jpg"></a></li>
        </ul>			
      </div>
    </div><!-- Social Media Bar -->

    </section>

  <!-- Footer -->
  <?php include("all_footer.php"); ?>

  </body>
</html>
