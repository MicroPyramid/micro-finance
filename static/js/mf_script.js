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
  //date picker
  $(function ()
  {
    $("#datepicker").datepicker(
    {
      showOtherMonths: true,
      selectOtherMonths: true
    });
  });
  $(function ()
  {
    $("#date-picker-gc").datepicker(
    {
      showOtherMonths: true,
      selectOtherMonths: true
    });
  });
  $(function ()
  {
    $("#date-picker-cc").datepicker(
    {
      showOtherMonths: true,
      selectOtherMonths: true
    });
  });

  //datepicker
  //slide togle
  $(".anc1").click(function ()
  {
    $("#tog-div1").slideToggle('slow', function ()
    {

      });
  });
  $(".anc2").click(function ()
  {
    $("#tog-div2").slideToggle('slow', function ()
    {

      });
  });
  $(".anc3").click(function ()
  {
    $("#tog-div3").slideToggle('slow', function ()
    {

      });
  });
  $(".anc4").click(function ()
  {
    $("#tog-div4").slideToggle('slow', function ()
    {

      });
  });
  //slide togle
  //ready function ended below
});