// JavaScript Document
$(document).ready(function (e)
{
  //text-box focus
  $(".text-box").focus(function (e)
  {
    $(this).css("background", "#e8f6f4")
  });
  $(".text-box").blur(function (e)
  {
    $(this).css("background", "#fff")
  });
  //text-box focus ends above
  //login form replace div
  $("#frgt-btn").click(function (e)
  {
    $(".login-form").css("display", "none")
    $(".reset-form").css("display", "block")
  });
  //login form replace div
  //slider toogle
  //slider toogle
  //ready function ended below
});

function toggleSlider()
{
  if ($("#panelThatSlides").is(":visible"))
  {
    $("#contentThatFades").animate(
    {
      opacity: "0"
    }, 600, function ()
    {
      $("#panelThatSlides").slideUp();
    });
  }
  else
  {
    $("#panelThatSlides").slideDown(600, function ()
    {
      $("#contentThatFades").animate(
      {
        opacity: "1"
      }, 600);
    });
  }
}