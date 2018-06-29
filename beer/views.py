from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect
from django.contrib.contenttypes.models import ContentType
from noctoz_common.models import Comment, CommentForm
from beer.models import Beer, BeerForm, Review, Brewery, BreweryForm, Town, TownForm, BeerRecipe, HopsRecipeEntry, MiscIngredientEntry, Hops, MaltRecipeEntry, BeerRecipeForm, NewBeerRecipeForm, PrimaryFermentation, SecondaryFermentation, PrimingEntry
from decimal import *
import math
from itertools import chain
import operator
import datetime

def index(request):
	beer_list = Beer.objects.all()
	t = loader.get_template('beer/index.html')
	c = RequestContext(request, {
		'beer_list': beer_list,
	})
	return HttpResponse(t.render(c))

def review(request, review_id):
	review = Review.objects.get(id=review_id)
	t = loader.get_template('beer/review.html')
	c = RequestContext(request, {
		'review': review,
	})
	return HttpResponse(t.render(c))

def beer(request, beer_id):
	beer = Beer.objects.get(id=beer_id)
	t = loader.get_template('beer/beer.html')
	c = RequestContext(request, {
		'beer': beer,
	})
	return HttpResponse(t.render(c))

@permission_required('beer.add_beer',  raise_exception=True)
def add_beer(request):
	next = ""
	if request.method == 'POST':
		next = request.POST["next"]
		
		try:
			edited_form = BeerForm(request.POST)
			edited_form.save()
		except Exception as e:
			return HttpResponse(e)

	return HttpResponseRedirect(next)

def brewery(request, brewery_id):
	brewery = Brewery.objects.get(id=brewery_id)
	t = loader.get_template('beer/brewery.html')
	c = RequestContext(request, {
		'brewery': brewery,
	})
	return HttpResponse(t.render(c))

@permission_required('beer.add_brewery',  raise_exception=True)
def add_brewery(request):
	next = ""
	if request.method == 'POST':
		next = request.POST["next"]
		try:
			edited_form = BreweryForm(request.POST)
			edited_form.save()
		except Exception as e:
			return HttpResponse(e)
	
	return HttpResponseRedirect(next)

@permission_required('beer.add_town',  raise_exception=True)
def add_town(request):
	next = ""
	if request.method == 'POST':
		next = request.POST["next"]
		try:
			edited_form = TownForm(request.POST)
			edited_form.save()
		except Exception as e:
			return HttpResponse(e)
	
	return HttpResponseRedirect(next)

def recipe_add_comment(request, recipe_id):
	recipe = BeerRecipe.objects.get(id=recipe_id)
	next = "/beer/recipe/%s/" % (recipe_id)
	if request.method == 'POST':
		try:
			comment = Comment(parent_object=recipe, author=request.user, pub_date=datetime.datetime.now())
			comment.save()
			edited_form = CommentForm(request.POST, instance=comment)
			edited_form.save()
		except Exception as e:
			return HttpResponse(e)
	
	return HttpResponseRedirect(next)

def recipes(request):
	if request.method == 'POST':
		try:
			if not request.user.has_perm('beer.add_beerrecipe'):
				return HttpResponse("You do not have the required permission to add a recipe")
			
			edited_form = NewBeerRecipeForm(request.POST)
			recipe = edited_form.save()
		except Exception as e:
			return HttpResponse(e)

	recipes = BeerRecipe.objects.all()
	recipe_form = NewBeerRecipeForm()
	beer_form = BeerForm()
	brewery_form = BreweryForm()
	town_form = TownForm()

	t = loader.get_template('beer/recipes.html')
	c = RequestContext(request, {
		'recipes': recipes,
		'recipe_form': recipe_form,
		'beer_form': beer_form,
		'brewery_form': brewery_form,
		'town_form': town_form,
	})

	return HttpResponse(t.render(c))

#@permission_required('beer.view_recipe')
def recipe(request, recipe_id):
	recipe = BeerRecipe.objects.get(id=recipe_id)
	
	if recipe.secret:
		if not request.user.is_authenticated():
			return redirect('/accounts/login/?next=%s' % request.path)
		if not request.user.has_perm('beer.view_recipe'):
			return redirect('/accounts/login/?next=%s' % request.path)

	if request.method == 'POST':
		print("Handling POST data")
		print(request.POST)
		try:
			print(recipe.final_volume)
			edited_form = BeerRecipeForm(request.POST, instance=recipe)
			print("form created")
			print(edited_form)
			recipe = edited_form.save()
		except Exception as e:
			print("Error posting:")
			print(e)
			return HttpResponse(e)

	og = float(recipe.og)
	fg = float(recipe.fg)
	
	ibu = 0
	ibu_tinseth_total = 0
	ibu_rager = 0
	
	final_volume = float(recipe.final_volume)

	ebc = 0
	oeshle = 0
	total_malt_weight = 0
	malt_entries = []
	malt_recipe_entries = MaltRecipeEntry.objects.filter(recipe_id=recipe_id)
	for entry in malt_recipe_entries:
		total_malt_weight += float(entry.amount)
		ebc += (float(entry.malt.ebc) * float(entry.amount))
		oeshle += float(entry.malt.malt_type.extract_potential) * float(entry.amount)
		extract_potential = (float(entry.malt.dbfg) - float(entry.malt.mc) - 0.002)
		water_malt_ratio = float(recipe.start_water_volume) / float(entry.amount)
		gravity = 0

		malt_entries.append({
			'malt_data': entry,
			'extract_potential': extract_potential,
		})

	extract_potential = 0
	for entry in malt_entries:
		extract_potential += ((float(entry['malt_data'].amount) / total_malt_weight) * entry['extract_potential'])

	# Compute boil and max volumes from start volume and malt data
	boil_volume = 0
	max_volume = 0
	water_malt_ratio = 0
	water_malt_ratio_boil = 0

	if float(recipe.start_water_volume) > 0 and total_malt_weight > 0:
		water_malt_ratio  = float(recipe.start_water_volume) / total_malt_weight
		boil_volume = float(recipe.start_water_volume) - (0.9 * total_malt_weight)
		max_volume = float(recipe.start_water_volume) + total_malt_weight
		water_malt_ratio_boil = boil_volume / total_malt_weight

	final_volume_estimate = boil_volume * 0.85
	if final_volume == 0:
		final_volume = final_volume_estimate

	# Compute SG from malt and water data together with our set conversion efficiency
	potential_sg_plato = 0
	potential_sg = 0
	pre_boil_sg_simple = 0
	pre_boil_sg_adjusted_plato = 0
	pre_boil_sg_adjusted = 0

	if water_malt_ratio_boil > 0:
		potential_sg_plato = 100.0 * ((extract_potential / 100.0) / (water_malt_ratio_boil + (extract_potential / 100.0)))
		potential_sg = 1.0 + (potential_sg_plato / 250.0)
		pre_boil_sg_simple = ((oeshle / boil_volume) / 1000.0) + 1.0
		pre_boil_sg_adjusted_plato = potential_sg_plato * (float(recipe.conversion_efficiency) / 100.0)
		pre_boil_sg_adjusted = 1.0 + (pre_boil_sg_adjusted_plato / 250.0)

	brewhouse_efficiency = float(recipe.conversion_efficiency) * float(recipe.lauter_efficiency)

	boil_final_ratio = 1
	
	if final_volume > 0:
		boil_final_ratio = boil_volume / final_volume
		ebc = 7.91 * math.pow(ebc / final_volume, 0.6859)
	else:
		ebc = 0

	yeast_amount = 0
	attenuation = 0
	cell_concentration = 0
	target_pitch_rate = 0
	fermationation_temp = 0
	fermentation_stages = PrimaryFermentation.objects.filter(recipe_id=recipe_id)
	for stage in fermentation_stages:
		yeast_amount = float(stage.yeast_amount)
		attenuation = float(stage.yeast.attenuation)
		cell_concentration = float(stage.yeast.cell_concentration)
		target_pitch_rate = float(stage.target_pitch_rate)
		fermationation_temp = float(stage.temp)

	og_potential = 1.0 + ((boil_final_ratio * potential_sg_plato) / 250.0)
	og_adjusted = 1.0 + ((boil_final_ratio * pre_boil_sg_adjusted_plato) / 250.0)
	fg_estimated2 = ((og_adjusted - 1.0) * (1.0 - (attenuation / 100.0))) + 1.0

	e = 0.003076925
	f = -1.32356731
	g = 1.317275958
	h = 0.002933349

	# Compute ABV from OG and FG estimates
	abv_estimated2 = 0

	if og_adjusted > 1 and fg_estimated2 > 1:
		abv_decimal = (e * og_adjusted + f) * fg_estimated2 + (g * og_adjusted + h)
		abv_estimated2 = abv_decimal * 100

	# Compute OG from SG and vice versa in case we did not measure either of those
	og_from_sg = 1.0
	if float(recipe.pre_boil_sg) > 0:
		og_from_sg = 1.0 + ((float(recipe.pre_boil_sg) - 1.0) * boil_final_ratio)
	sg_from_og = 1.0
	if og > 0 and boil_final_ratio > 0:
		sg_from_og = 1.0 + ((og - 1.0) / boil_final_ratio)

	pre_boil_sg = float(recipe.pre_boil_sg)
	if pre_boil_sg == 0:
		pre_boil_sg = sg_from_og
	if pre_boil_sg == 0:
		pre_boil_sg = pre_boil_sg_adjusted

	# We want to set og to the most accuracte value.
	# Use set value from database if available, then computed value from pre-boil SG, then fully computer value.
	if og == 0:
		og = og_from_sg

	# Compute FG, ABV and brewhouse efficiency from database OG or OG computed from database SG
	fg_estimated = 0
	computed_brewhouse_eff = 0
	abv_estimated = 0

	if og > 0:
		fg_estimated = ((og - 1.0) * (1.0 - (attenuation / 100.0))) + 1.0
		abv_decimal = (e * og + f) * fg_estimated + (g * og + h)
		abv_estimated = abv_decimal * 100

		if og_potential > 1:
			computed_brewhouse_eff = ((og - 1.0) / (og_potential - 1.0)) * 100

	# Compute ABV and attenuation from database OG and FG
	apparent_attenuation = 0
	abv_approx = 0
	abv = 0

	if og > 0 and fg > 0:
		apparent_attenuation = 100.0 - (((fg - 1.0) / (og - 1.0)) * 100.0)
		abv_approx_dec = (og - fg) * 1.31
		abv_approx = abv_approx_dec * 100

		abv_decimal = (e * og + f) * fg + (g * og + h)
		abv = abv_decimal * 100

	hops_entries = []

	#hops_recipe_entries = HopsRecipeEntry.objects.filter(recipe_id=recipe_id).order_by('add_time')
	qs1 = HopsRecipeEntry.objects.filter(recipe_id=recipe_id)
	qs2 = MiscIngredientEntry.objects.filter(recipe_id=recipe_id)
	boil_recipe_entries = sorted(chain(qs1, qs2), key = operator.attrgetter('add_time'))
	
	for entry in boil_recipe_entries:
		ibu_for_hops = 0
		is_hops = False
	
		if isinstance(entry, HopsRecipeEntry):
			is_hops = True
			
			if final_volume > 0:
				boil_time = 60 - entry.add_time
		
				milligrames_per_litre = (entry.amount * 1000) / final_volume
				alpha_per_litre = milligrames_per_litre * (float(entry.hops.alpha) / 100)
				contrib_per_litre = 0
				if entry.hops.hops_type == 'pellets':
					contrib_per_litre = alpha_per_litre * (40 / 100)
				else:
					contrib_per_litre = alpha_per_litre * (30 / 100)
					ibu_temp = contrib_per_litre * (boil_time / 60.0)
					ibu += ibu_temp
		
				bigness_factor = 1.65 * math.pow(0.000125, pre_boil_sg - 1.0)
				boil_time_factor = 1 - math.exp(-0.04 * boil_time)
				alpha_utilization = bigness_factor * boil_time_factor / 4.15
				ibu_tinseth = alpha_per_litre * alpha_utilization
				if entry.hops.hops_type == 'pellets':
					ibu_tinseth = ibu_tinseth * 1.1
				ibu_tinseth_total += ibu_tinseth
		
				util = (18.11 + 13.86 * math.tanh((boil_time - 31.32) / 18.27)) / 100
				ibu_temp = alpha_per_litre * util
				ibu_rager += ibu_temp
		
				ibu_for_hops = ibu_tinseth
	
		hops_entries.append({
			'is_hops': is_hops,
			'recipe_entry': entry,
			'ibu': ibu_for_hops,
		})


	plato_times_volume = 0
	if og > 0:
		plato_times_volume = (259 - (259 / og)) * final_volume

	yeast_cells_needed = plato_times_volume * target_pitch_rate
	if cell_concentration > 0:
		dry_yeast_needed = yeast_cells_needed / cell_concentration
	else:
		dry_yeast_needed = 0

	computed_pitch_rate = 0
	if plato_times_volume > 0:
		computed_pitch_rate = (cell_concentration * yeast_amount) / plato_times_volume
	
	carbon_dioxide_concentration = 0.0
	priming_entries = PrimingEntry.objects.filter(recipe_id=recipe_id)
	for entry in priming_entries:
		carbon_dioxide_concentration = float(entry.carbon_dioxide_concentration)

	temp_f = fermationation_temp * 1.8 + 32

	final_volume_gallons = final_volume * 0.264172052

	priming_sugar = 15.195 * final_volume_gallons * (carbon_dioxide_concentration - 3.0378 + (0.050062 * temp_f) - (0.00026555 * math.pow(temp_f, 2)))

	form = BeerRecipeForm(instance=recipe)

	recipe_type = ContentType.objects.get_for_model(recipe)
	comments = Comment.objects.filter(content_type__pk=recipe_type.id, object_id=recipe.id)
	comment_form = CommentForm()

	t = loader.get_template('beer/recipe.html')
	c = RequestContext(request, {
		'recipe': recipe,
		'malt_entries': malt_entries,
		'hops_entries': hops_entries,
		'ebc': ebc,
		'boil_volume': boil_volume,
		'max_volume': max_volume,
		'final_volume_estimate': final_volume_estimate,
		'water_malt_ratio': water_malt_ratio_boil,
		'extract_potential': extract_potential,
		'og_potential': og_potential,
		'og_adjusted': og_adjusted,
		'potential_sg': potential_sg,
		'pre_boil_sg': pre_boil_sg,
		'pre_boil_sg_simple': pre_boil_sg_simple,
		'pre_boil_sg_adjusted': pre_boil_sg_adjusted,
		'og_from_sg': og_from_sg,
		'sg_from_og': sg_from_og,
		'fg_estimated': fg_estimated,
		'fg_estimated2': fg_estimated2,
		'computed_brewhouse_eff': computed_brewhouse_eff,
		'fermentation_stages': fermentation_stages,
		'ibu': ibu,
		'ibu_tinseth': ibu_tinseth_total,
		'ibu_rager': ibu_rager,
		'abv_approx': abv_approx,
		'abv': abv,
		'abv_estimated': abv_estimated,
		'abv_estimated2': abv_estimated2,
		'yeast_cells_needed': yeast_cells_needed,
		'dry_yeast_needed': dry_yeast_needed,
		'apparent_attenuation': apparent_attenuation,
		'computed_pitch_rate': computed_pitch_rate,
		'priming_entries': priming_entries,
		'priming_sugar': priming_sugar,
		'form': form,
		'comments': comments,
		'comment_form': comment_form,
	})
	return HttpResponse(t.render(c))