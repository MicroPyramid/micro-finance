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
  //ready function ended below
});