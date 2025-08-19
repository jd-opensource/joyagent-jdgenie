import { readable } from 'svelte/store';
import * as constants from '$lib/utils/constants';

// Create a readable store for constants
export const constantsStore = readable(constants);